from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import numpy as np
import nltk

#Initialize Flask instance
app = Flask(__name__)

example_data = [
    {'name': 'Cat sleeping on a bed', 'source': 'cat.jpg'},
    {'name': 'Misty forest', 'source': 'forest.jpg'},
    {'name': 'Bonfire burning', 'source': 'fire.jpg'},
    {'name': 'Old library', 'source': 'library.jpg'},
    {'name': 'Sliced orange', 'source': 'orange.jpg'}
]

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

    gv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2", token_pattern=r'(?u)\b\w+\b', ngram_range=(number, number))
    g_matrix = gv.fit_transform(doc_split).T.tocsr()

    # Vectorize query string
    query_vec = gv.transform([query_string]).tocsc()

    # Cosine similarity
    hits = np.dot(query_vec, g_matrix)

    # Rank hits
    try:
        ranked_scores_and_doc_ids = \
        sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]),
               reverse=True)
        # Output result
        #print("Your query '{:s}' matches the following documents:".format(query_string))
        # for i, (score, doc_idx) in enumerate(ranked_scores_and_doc_ids):
        #     print("Doc #{:d} (score: {:.4f}): {:s}".format(i+1, score, names[doc_idx]))
        # #print()
    except IndexError:

        print("No matching documents found.")
    return ranked_scores_and_doc_ids

#Function search() is associated with the address base URL + "/search"
@app.route('/search')
def search():
    matches = []
    #Get query from URL variable
    number = request.args.get('number')

    words = request.args.get('words')

    #Initialize list of matches

    #If query exists (i.e. is not None)
    # if len(number) != 0: # if empty line then stops the program
    #     try:
    #         number = int(number)
    #     except:
    #         number = 0

    if number and words: # if user inputs a zero, a negative or a non-integer number, asks for a valid number
        # print("Invalid input. Please enter a number larger than 0.")
            # if the number is valid
        number = int(number)
        for w in words.split(): # separates input into words
            # if a word (letters separated by non-letters) is not in the documents, informs user of the unknown word(s)
            if w not in set(re.split("\W", (" ".join(y.lower() for y in doc_split)))) or w[-2:] == "'s":
                # if w[-2:] == "'s": # if user searches kfor word with possessive suffix, show appropriate message
                #     # print("Write possessive suffixes as separate words without an apostrophe.")
                # else: # otherwise tells user which word(s) is/are unknown
                #     # print("\"{:s}\" is an unknown word.".format(w))
                words = " ".join([word for word in words.split() if word != w]) # deletes unknown words from input
                number -= 1 # decreases the user's number according to the number of unknown words
                # if the input does not consist only of unknown words
             # if the number entered is not larger than the number of words
        matches = search_article(words, number) # search normally
                # else:
                #     print("Wrong number of words.")


    #Render index.html with matches variable
    return render_template('index.html', matches=matches)
