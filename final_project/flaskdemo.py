# # Suvin versio
#
#

import xml.etree.ElementTree as ET
import os
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import numpy as np
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import tokenize

#Initialize Flask instance
app = Flask(__name__)

# both parser() and open_file() have time complexity On^2 because of the loops - because of this the code is quite slow (30s) when it goes through the large genres, such as Action.
# otherwise the code works in tolerable speed.

def parser(polku):
    tree = ET.parse(polku)
    root = tree.getroot()

    subtitle = " " # creates an empty string

    for elem in root: # the loop goes through the XML tree
        for subelem in elem:
            if subelem.text != None:
                subtitle = subtitle + " " + subelem.text # adds all the words of the file into the string if the value of the word is not None
    return subtitle

def open_file(genre):
    subtitles = []
    names = []

    root_path = r"static\en\OpenSubtitles\xml\en"
    directory = os.path.join(root_path, genre)

    years = []

    for filename in os.listdir(directory):

        years.append(filename)


    for year in years:
        folder = os.path.join(directory, year)
        for filename in os.listdir(folder):

            if filename.endswith(".xml"):
                names.append(filename)
                path = os.path.join(folder, filename)

                subtitles.append(parser(path))



    return subtitles, names

def manipulate(list):
    new_list = []
    for item in list:

        new_item = re.sub(r"\d*_\d*_\d*_(.*)\.xml", r"\1", item)
        new_item = " ".join(x for x in new_item.split("_"))
        if new_item not in new_list:
            new_list.append(new_item)
    return new_list



def search_article(query_string, number, doc, names):
    match_names = []
    merror = False
    gv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2", token_pattern=r'(?u)\b\w+\b', ngram_range=(number, number))
    g_matrix = gv.fit_transform(doc).T.tocsr()

    # Vectorize query string
    query_vec = gv.transform([query_string]).tocsc()

    hits = np.dot(query_vec, g_matrix)

    # Rank hits
    ranked_scores_and_doc_ids = \
    sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]),
           reverse=True)
    # Output result
    for i, (score, doc_idx) in enumerate(ranked_scores_and_doc_ids):
         match_names.append(names[doc_idx])

    match_names = manipulate(match_names)

    return match_names

def stem_search(query_string, number): # stem search as a separate function (if we can make it work it might be possible to implement it to the previous search function)
    match_names, match_starts = [], []
    merror = False
    gv = TfidfVectorizer(tokenizer=tokenize, lowercase=True, sublinear_tf=True, use_idf=True, norm="l2", token_pattern=r'(?u)\b\w+\b', ngram_range=(number, number))
    g_matrix = gv.fit_transform(doc_split).T.tocsr()

    snow_stemmer = SnowballStemmer(language='english')
    for w in gv:
        x = snow_stemmer.stem(w)
        stem_words.append(x)
    stemmed_text = " ".join(stem_words)

    # Vectorize query string
    query_vec = gv.transform([stemmed_text]).tocsc()

    # Cosine similarity
    hits = np.dot(stemmed_text, g_matrix)

    for i, (score, doc_idx) in enumerate(ranked_scores_and_doc_ids):
         match_names.append(names[doc_idx])
         match_starts.append(doc_split[doc_idx][:100])
    return list(zip(match_names,match_starts))


#Function search() is associated with the address base URL + "/search"
@app.route('/search', methods=['GET', 'POST'])
def search():
    errors =[]
    all_articles = {}
    number = int(number)
    #Get queries from URL variable
    if request.method == "POST":
        genres = request.form.getlist('genre')
        number = request.form.get('number')
        words = request.form.get('words')

    # if number and words: # if the user has entered something in both fields
    #     try:
    #         number = int(number) # converts the number into an integer
    #     except:
    #         number = 0
    #     if number <= 0:
    #         errors = ["Invalid input. Please enter an integer larger than 0."]
    #     else:
    #         for w in words.split(): # separates input into words
    #             # if a word (letters separated by non-letters) is not in the documents, informs user of the unknown word(s)
    #             if w not in set(re.split("\W", (" ".join(y.lower() for y in doc_split)))) or w[-2:] == "'s":
    #                 errors.append("") # add dummy item to errors list for the html to know to still show articles
    #                 if w[-2:] == "'s": # if user searches for word with possessive suffix, show appropriate message
    #                     errors.append("Write possessive suffixes as separate words without an apostrophe.")
    #                 else: # otherwise tells user which word(s) is/are unknown
    #                     errors.append("\"{:s}\" is an unknown word.".format(w))
    #                 words = " ".join([word for word in words.split() if word != w]) # deletes unknown words from input
    #                 number -= 1 # decreases the user's number according to the number of unknown words
    #         if len(words) != 0: # if the input does not consist only of unknown words
    #             if number <= 0 and len(words.split()) != 0: # if the resulting number is 0 or less but there is at least 1 known word
    #                 number = len(words.split()) # correct the number
    #             try:
    #                 if number <= len(words.split()): # if the number entered is not larger than the number of words
    #                     articles = search_article(words, number) # search normally
    #                 else:
    #                     errors = ["Wrong number of words."]


     #if the user has entered something in both fields
     #try:
    number = int(number) # converts the number into an integer
    if number <= 0:
        errors = ["Invalid input. Please enter an integer larger than 0."]
    else:
        for w in words.split(): # separates input into words
        # if a word (letters separated by non-letters) is not in the documents, informs user of the unknown word(s)
            if w not in set(re.split("\W", (" ".join(y.lower() for y in subtitles)))) or w[-2:] == "'s":
                errors.append("") # add dummy item to errors list for the html to know to still show articles
                #         if w[-2:] == "'s": # if user searches for word with possessive suffix, show appropriate message
                #             errors.append("Write possessive suffixes as separate words without an apostrophe.")
            else: # otherwise tells user which word(s) is/are unknown
                errors.append("\"{:s}\" is an unknown word.".format(w))
        words = " ".join([word for word in words.split() if word != w]) # deletes unknown words from input
        number -= 1 # decreases the user's number according to the number of unknown words
        print(request.form)
        if len(words) > 0: # if the input does not consist only of unknown words
            if number <= 0 and len(words.split()) > 0: # if the resulting number is 0 or less but there is at least 1 known word
                number = len(words.split()) # correct the number
            try:
                if len(genres) == 0:
                    errors = ["Select at least one genre"]
                else:   # if number <= len(words.split()): # if the number entered is not larger than the number of words

                    for genre in genres:
                        doc, names = open_file(genre)
                        articles = search_article(words, number, doc, names) # search normally
                        all_articles[genre] = articles
                        # else:
                        #     errors = ["Wrong number of words."]
            except IndexError:
                errors = ["No matching documents found."]

        else:
            errors = ["Enter both a number and at least one word."]


    #Render index.html with matches variable
    print(all_articles)
    return render_template('index.html', articles=all_articles, errors=errors)
