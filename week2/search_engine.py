from sklearn.feature_extraction.text import CountVectorizer
import re

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
    doc_split = re.split("</?article.*>", doc)

    f_lines.close()
    f_string.close()

except FileNotFoundError:
    print("File cannot be read")


# documents = ["This is a silly example",
#             "A better example this",
#             "Nothing to this see here",
#             "This is a great and long example"]

cv = CountVectorizer(lowercase=True, token_pattern = r"(?u)\b\w+\b", binary=True)
sparse_matrix = cv.fit_transform(doc_split)
dense_matrix = sparse_matrix.todense()
td_matrix = dense_matrix.T

sparse_td_matrix = sparse_matrix.T.tocsr()

t2i = cv.vocabulary_  # shorter notation: t2i = term-to-index

d = {"AND": "&",
     "OR": "|",
     "NOT": "1 -",
     "(": "(", ")": ")"}          # operator replacements

def rewrite_token(t):
    return d.get(t, 'sparse_td_matrix[t2i["{:s}"]].todense()'.format(t))

def rewrite_query(query): # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())

def test_query(query):
    print("Query: '" + query + "'")
    print("Rewritten:", rewrite_query(query))
    print("Matching:", eval(rewrite_query(query))) # Eval runs the string as a Python command
    print()

while True:
    y = True
    print("Enter a word (empty line stops the program). Put operators in capitals.")
    x = input()
    if len(x) == 0:
        break
    elif x not in set(re.split("\W|-", (" ".join(z.lower() for z in doc_split)))):
        print("Unknown word")
        print()
        y = False
    if y:
        test_query(x)

        hits_matrix = eval(rewrite_query(x))

        hits_list = list(hits_matrix.nonzero()[1])

        print("The word is in ", len(hits_list), "articles")
        for i, doc_idx in enumerate(hits_list[:10]):
            print("The name of the article {}: {}".format(i+1, names[(int(doc_idx) - 1) // 2]))
            print("Preview: {:.500}...".format(doc_split[doc_idx]))
            print()
