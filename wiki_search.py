import json
import sys
import re
import Stemmer
from nltk.corpus import stopwords

stemmer = Stemmer.Stemmer("porter")

STOP_WORDS = set(stopwords.words("english"))
# print(type(STOP_WORDS))
STOP_WORDS.add("cite")
STOP_WORDS.add("redirect")

inverted_index = {}
query = ""

def tokenize(data):
    return re.split(r"[^A-Za-z0-9]+", str(data))
    
def preprocess(data):
    return [stemmer.stemWord(token.casefold()) for token in tokenize(data) if token and token.casefold() not in STOP_WORDS]

def plain_query(query):
    tokens = preprocess(query)

    for token in tokens:
        if token not in inverted_index:
            # print(f"{token}: ")
            pass
        
        else:
            print(f"{token}: {inverted_index[token]}")

def field_query(query):
    queries = query.split(":")
    length = len(queries)
    field = ""

    for i, query in enumerate(queries):

        if i == length - 1:
            tokens = preprocess(query)

            for token in tokens:
                if token in inverted_index:
                    postings = inverted_index[token]

                    if field in postings:
                        print(f"{token}: {postings}")
            
            return

        if field.strip():
            new_field = query[-1]
            new_query = query[:-1]

            tokens = preprocess(new_query)

            for token in tokens:
                if token in inverted_index:
                    postings = inverted_index[token]

                    if field in postings:
                        print(f"{token}: {postings}")
            
            field = new_field

        else:
            field = query[-1]

            if len(query) > 1:
                new_query = query[:-1]

                tokens = preprocess(new_query)

                for token in tokens:
                    if token in inverted_index:
                        print(f"{token}: {inverted_index[token]}")


if __name__ == "__main__":

    with open(f"{sys.argv[1]}/inverted_index.json", "r") as fp:
        inverted_index = json.load(fp)

    query = sys.argv[2]

    if ":" in query:
        field_query(query)
    
    else:
        plain_query(query)