from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import numpy as np
import nltk

#Initialize Flask instance
app = Flask(__name__)

def open_file():
    names = []

    f_lines = open(r"static/enwiki-20181001-corpus.100-articles.txt", encoding="utf-8") # the code opens the same file twice because I couldn't find any other way to handle the file both as a string and a txt file that contains lines
    f_string = open(r"static/enwiki-20181001-corpus.100-articles.txt", encoding="utf-8")

    for line in f_lines: # to use single lines of the file the text can't be a string
        if "<article" in line:
            line_split = line.split("\"")
            name = line_split[1]
            names.append(name)

    doc = f_string.read() # the re.split function on the other hand needs a string
    doc_split = [art for art in re.split("</?article.*>", doc) if len(art)>2] # takes only actual, non-empty articles


    f_lines.close()
    f_string.close()

    return doc_split, names
doc_split, names = open_file()

def search_article(query_string, number):
    scores, match_names, match_starts = [], [], []
    gv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2", token_pattern=r'(?u)\b\w+\b', ngram_range=(number, number))
    g_matrix = gv.fit_transform(doc_split).T.tocsr()

    # Vectorize query string
    query_vec = gv.transform([query_string]).tocsc()

    # Cosine similarity
    hits = np.dot(query_vec, g_matrix)

    # Rank hits
    ranked_scores_and_doc_ids = \
    sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]),
           reverse=True)
    # Output result
    for i, (score, doc_idx) in enumerate(ranked_scores_and_doc_ids):
        scores.append(float("{:4f}".format(score)))
        match_names.append(names[doc_idx])
        match_starts.append(doc_split[doc_idx][:100])
    return list(enumerate(zip(scores,zip(match_names,match_starts))))

#Function search() is associated with the address base URL + "/search"
@app.route('/search')
def search():
    articles, errors = [],[]
    #Get queries from URL variable
    number = request.args.get('number')
    searchtype = request.args.get('searchtype')
    words = request.args.get('words')

    if number and words: # if the user has entered something in both fields
        number = int(number)
        for w in words.split(): # separates input into words
            # if a word (letters separated by non-letters) is not in the documents, informs user of the unknown word(s)
            if w not in set(re.split("\W", (" ".join(y.lower() for y in doc_split)))) or w[-2:] == "'s" or "-" in w:
                errors.append("") # add dummy item to errors list for the html to know to still show articles
                if w[-2:] == "'s": # if user searches for word with possessive suffix, show appropriate message
                    errors.append("Write possessive suffixes as separate words without an apostrophe.")
                elif "-" in w:
                    errors.append("Write hyphenated words separately.")
                else: # otherwise tells user which word(s) is/are unknown
                    errors.append("\"{:s}\" is an unknown word.".format(w))
                words = " ".join([word for word in words.split() if word != w]) # deletes unknown words from input
                number -= 1 # decreases the user's number according to the number of unknown words
        if len(words) != 0: # if the input does not consist only of unknown words
            if number <= 0 and len(words.split()) != 0: # if the resulting number is 0 or less but there is at least 1 known word
                number = len(words.split()) # correct the number
            try:
                if number <= len(words.split()): # if the number entered is not larger than the number of words
                    articles = search_article(words, number) # search normally
                else:
                    errors = ["Wrong number of words."]
            except IndexError:
                pass

    else:
        errors = ["Enter both a number and at least one word."]

    #Render index.html with matches variable
    return render_template('index.html', articles=articles, errors=errors, searchtype=searchtype)
