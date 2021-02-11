from sklearn.feature_extraction.text import TfidfVectorizer
import re
import numpy as np
import nltk

def open_file():
    names = []
    try:
        f_lines = open(r"enwiki-20181001-corpus.100-articles.txt", encoding="utf-8") # the code opens the same file twice because I couldn't find any other way to handle the file both as a string and a txt file that contains lines
        f_string = open(r"enwiki-20181001-corpus.100-articles.txt", encoding="utf-8")

        for line in f_lines: # to use single lines of the file the text can't be a string
            if "<article" in line:
                line_split = line.split("\"")
                name = line_split[1]
                names.append(name)

        doc = f_string.read() # the re.split function on the other hand needs a string
        doc_split = [art for art in re.split("</?article.*>", doc) if len(art)>2] # takes only actual, non-empty articles
        return names, doc_split

        f_lines.close()
        f_string.close()

    except FileNotFoundError:
        print("File cannot be read")

names, doc_split = open_file()

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
        print("Your query '{:s}' matches the following documents:".format(query_string))
        for i, (score, doc_idx) in enumerate(ranked_scores_and_doc_ids):
            print("Doc #{:d} (score: {:.4f}): {:s}".format(i+1, score, names[doc_idx]))
        print()
    except IndexError:
        print("No matching documents found.")

while True:
    x = True
    print("\nGive the number of words you want to search. Keep in mind:\n -Empty line stops the program.\n",
        "-If you want to search for the words separately, put \"1\"; for pairs of words, put \"2\", etc.")
    number = input("Number: ")
    if len(number) != 0: # if empty line then stops the program
        try:
            number = int(number)
        except:
            number = 0
    else:
        break
    if number <= 0: # if user inputs a zero, a negative or a non-integer number, asks for a valid number
        print("Invalid input. Please enter a number larger than 0.")
    else: # if the number is valid
        inp = input("Enter search word(s): ")
        for w in inp.split(): # separates input into words
            # if a word (letters separated by non-letters) is not in the documents, informs user of the unknown word(s)
            if w not in set(re.split("\W", (" ".join(y.lower() for y in doc_split)))) or w[-2:] == "'s":
                if w[-2:] == "'s": # if user searches for word with possessive suffix, show appropriate message
                    print("Write possessive suffixes as separate words without an apostrophe.")
                else: # otherwise tells user which word(s) is/are unknown
                    print("\"{:s}\" is an unknown word.".format(w))
                inp = " ".join([word for word in inp.split() if word != w]) # deletes unknown words from input
                number -= 1 # decreases the user's number according to the number of unknown words
        if len(inp) != 0: # if the input does not consist only of unknown words
            if number <= 0 and len(inp.split()) != 0: # if the resulting number is 0 or less but there is at least 1 known word
                number = len(inp.split()) # correct the number
            try:
                if number <= len(inp.split()): # if the number entered is not larger than the number of words
                    search_article(inp, number) # search normally
                else:
                    print("Wrong number of words.")
            except:
                continue
