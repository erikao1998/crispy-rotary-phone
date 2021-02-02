from sklearn.feature_extraction.text import CountVectorizer

documents = ["This is a silly example",
             "A better example this",
             "Nothing to this see here",
             "This is a great and long example"]

cv = CountVectorizer(lowercase=True, token_pattern = r"(?u)\b\w+\b", binary=True)
sparse_matrix = cv.fit_transform(documents)
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
    x = input("enter a word (empty line stops the program): ")
    if len(x) == 0:
        break
    elif x not in set((" ".join(z.lower() for z in documents)).split()):
        print("unknown word")
        y = False
    if y:
        test_query(x)

        hits_matrix = eval(rewrite_query(x))
        print("Matching documents as vector (it is actually a matrix with one single row):", hits_matrix)
        print("The coordinates of the non-zero elements:", hits_matrix.nonzero())

        hits_list = list(hits_matrix.nonzero()[1])

        for i, doc_idx in enumerate(hits_list):
            print("Matching doc #{:d}: {:s}".format(i, documents[doc_idx]))
