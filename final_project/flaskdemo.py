import xml.etree.ElementTree as ET
import os
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
import xml.etree.ElementTree as ET
import os, re, nltk
import numpy as np
from nltk.stem.snowball import SnowballStemmer
from nltk import tokenize

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
                subtitle += " " + subelem.text # adds all the words of the file into the string
    return subtitle


# def open_file(genre, selected_years):
def open_file():
    dict = {}
    genres = ["Fantasy", "Animation", "Horror"]
    for genre in genres:
        root_path = r"static\en\OpenSubtitles\xml\en"
        directory = os.path.join(root_path, genre)
        values = []

        for year in os.listdir(directory):
            folder = os.path.join(directory, year)
            x = []
            for filename in os.listdir(folder):

                if filename.endswith(".xml"):
                    path = os.path.join(folder, filename)
                    x.append([filename, parser(path), year])

            values.append((year, x))
        dict[genre] = values

    return dict


# removes every extra character from the titles of the matching movies
def manipulate(names, subtitles, years):
    new_list = []
    preview_list = []
    new_years = []
    for i in range(len(names)):
        new_item = re.sub(r"\d*_\d*_\d*_(.*)\.xml", r"\1", names[i]) # removes numbers and the file type
        new_item = " ".join(x for x in new_item.split("_")) # removes underscores that separated the parts of the title
        if new_item not in new_list: # prevents duplicates (that otherwise are quite common)
            new_list.append(new_item)
            preview_list.append(subtitles[i][0:200])
            new_years.append(years[i])
    return new_list, preview_list, new_years


dict = open_file()


def select_movies(genre, years):
    names = []
    subtitles = []
    selected_years = []
    for key in dict:
        if key == genre:
            for item in dict[key]:
                if item[0] in years:
                    for subtitle in item[1]:

                        names.append(subtitle[0])
                        subtitles.append(subtitle[1])
                        selected_years.append(subtitle[2])

    return subtitles, names, selected_years


def search_article(query_string, number, doc, names, stemmed, years):
    match_names = []
    subtitles = []
    match_years = []
    matches_and_previews = []

    gv = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2", token_pattern=r'(?u)\b\w+\b', ngram_range=(number, number))
    g_matrix = gv.fit_transform(stemmed).T.tocsr()

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
         subtitles.append(doc[doc_idx])
         match_years.append(years[doc_idx])

    match_names, subtitles, match_years = manipulate(match_names, subtitles, match_years)

    for i in range(len(match_names)):
        matches_and_previews.append([match_names[i], subtitles[i], match_years[i]])

    return matches_and_previews


def stem_search(doc, input): # stem search as a separate function (if we can make it work it might be possible to implement it to the previous search function)
    stem_words, stemmed_input = [], []
    snow_stemmer = SnowballStemmer(language='english')
    for w in doc:
        for word in w.split():
            x = snow_stemmer.stem(word)
            stem_words.append(x)
        stemmed_text = " ".join(stem_words)
        stem_words.append(stemmed_text)

    for w in input.split():
        x = snow_stemmer.stem(w)
        stemmed_input.append(x)

    return stem_words, stemmed_input


# Function search() is associated with the address base URL + "/search"
# Had some problems with multiword search so currently works only with one word
@app.route('/search', methods=['GET', 'POST']) # added POST and GET methods
def search():
    fantasy = [1966, 1983, 1984, 1985, 1995, 1998, 1999, 2000, 2001, 2005]
    animation = [1937, 1940, 1942, 1959, 1963, 1972, 1982, 1984, 1987, 1988, 1989, 1991, 1992, 1994, 1995, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005]
    horror = [1922, 1955, 1957, 1968, 1974, 1976, 1980, 1981, 1986, 1987, 1988, 1990, 1993, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005]
    errors, all_years, searchtype, matches = [],[],"",0
    all_articles = {} # created a dictionary instead of an array
    # the browser does a post request to the server when the user presses submit button.
    if request.method == "POST":
        searchtype = request.form.get('searchtype')
        genres = request.form.getlist('genre')
        number = request.form.get('number')
        words = request.form.get('words')
        fantasy_year = request.form.getlist('fantasy_year')
        animation_year = request.form.getlist('animation_year')
        horror_year = request.form.getlist('horror_year')

        if len(fantasy_year) > 0 and "Fantasy" in genres:
            all_years.append(fantasy_year)
        if len(animation_year) > 0 and "Animation" in genres:
            all_years.append(animation_year)
        if len(horror_year) > 0 and "Horror" in genres:
            all_years.append(horror_year)

     #if the user has entered something in both fields
        if number and words and len(genres) > 0 and len(all_years) >= len(genres):
            for x in range(len(genres)):
                all_docs, all_names, selected_years = select_movies(genres[x], all_years[x])
            number = int(number)# converts the number into an integer
            for w in words.split(): # separates input into words
                # if a word (letters separated by non-letters) is not in the documents, informs user of the unknown word(s)
                if w not in set(re.split("\W", (" ".join(subs.lower() for d in all_docs for subs in d.split())))) \
                 or w[-2:] == "'s" or "-" in w:
                    errors.append("") # add dummy item to errors list for the html to know to still show articles
                    if w[-2:] == "'s": # if user searches for word with possessive suffix, show appropriate message
                        errors.append("Write possessive suffixes as separate words without an apostrophe.")
                    elif "-" in w:
                        errors.append("Write hyphenated words separately.")
                    else: # otherwise tells user which word(s) is/are unknown
                        errors.append("\"{:s}\" is an unknown word.".format(w))
                    words = " ".join([word for word in words.split() if word != w]) # deletes unknown words from input
                    number -= 1 # decreases the user's number according to the number of unknown words
            if len(words) > 0:
                if number <= 0 and len(words.split()) > 0:
                    number = len(words.split())
                try:
                    if number <= len(words.split()):
                        for x in range(len(genres)):
                            subtitles, names, years = select_movies(genres[x], all_years[x])

                            if searchtype=="stem":
                                stemmed_text, words = stem_search(subtitles, words)
                            else:
                                stemmed_text=subtitles
                            articles = search_article(words, number, subtitles, names, stemmed_text, years)
                            matches += len(articles)
                            all_articles[genres[x]] = articles
                    else:
                        errors = ["Enter at least as many words as the number entered in the \"Number of words\" field."]
                except IndexError:
                    pass
        else:
            if len(genres) == 0:
                errors = ["Select at least one genre"]
            elif len(all_years) < len(genres):
                errors = ["Select at least one year for the selected genres"]
            else:
                errors = ["Enter both a number and at least one word."]

    #Render index.html with matches variable
    return render_template('index.html', searchtype=searchtype, articles=all_articles, errors=errors, \
            fantasy_years=fantasy, animation_years=animation, horror_years=horror, matches=matches)
