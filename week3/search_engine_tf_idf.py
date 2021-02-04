from sklearn.feature_extraction.text import TfidfVectorizer
import re

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
        doc_split = [art for art in re.split("</?article.*>", doc) if len(art)>2]
        return names, doc_split

        f_lines.close()
        f_string.close()

    except FileNotFoundError:
        print("File cannot be read")


# documents = ["This is a silly example",
#             "A better example this",
#             "Nothing to this see here",
#             "This is a great and long example"]
names, doc_split = open_file()

gv = TfidfVectorizer(lowercase=True, sublinear_tf=False, use_idf=False, norm=None)
tf_matrix1 = gv.fit_transform(doc_split).T.todense()

print("TfidfVectorizer:")
print(tf_matrix1)

print("\nCountVectorizer:")
print(dense_matrix)

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

while True:
    x = True
    print("Enter a word (empty line stops the program). Put operators in capitals.")
    inp = input()
    if len(inp) == 0:
        break
    for w in [y for y in inp.split() if y not in d]:
        if w not in set(re.split("\W|-", (" ".join(z.lower() for z in doc_split)))):
            print("\"{:s}\" is an unknown word.".format(w))
            print()
            x = False
    if x:
        hits_matrix = eval(rewrite_query(inp))

        hits_list = list(hits_matrix.nonzero()[1])

        print("The word is in ", len(hits_list), "articles")
        for i, doc_idx in enumerate(hits_list[:10]):
            print("The name of the article {}: {}".format(i+1, names[(int(doc_idx))]))
            print("Preview: {:.500}...".format(doc_split[doc_idx]))
            print()
