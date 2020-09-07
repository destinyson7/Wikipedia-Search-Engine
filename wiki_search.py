import json
import sys
import re
import Stemmer
import bisect
import math
from collections import defaultdict
import time

stemmer = Stemmer.Stemmer("english")

STOP_WORDS = set(['whence', 'here', 'show', 'were', 'why', 'n’t', 'the', 'whereupon', 'not', 'more', 'how', 'eight', 'indeed', 'i', 'only', 'via', 'nine', 're', 'themselves', 'almost', 'to', 'already', 'front', 'least', 'becomes', 'thereby', 'doing', 'her', 'together', 'be', 'often', 'then', 'quite', 'less', 'many', 'they', 'ourselves', 'take', 'its', 'yours', 'each', 'would', 'may', 'namely', 'do', 'whose', 'whether', 'side', 'both', 'what', 'between', 'toward', 'our', 'whereby', "'m", 'formerly', 'myself', 'had', 'really', 'call', 'keep', "'re", 'hereupon', 'can', 'their', 'eleven', '’m', 'even', 'around', 'twenty', 'mostly', 'did', 'at', 'an', 'seems', 'serious', 'against', "n't", 'except', 'has', 'five', 'he', 'last', '‘ve', 'because', 'we', 'himself', 'yet', 'something', 'somehow', '‘m', 'towards', 'his', 'six', 'anywhere', 'us', '‘d', 'thru', 'thus', 'which', 'everything', 'become', 'herein', 'one', 'in', 'although', 'sometime', 'give', 'cannot', 'besides', 'across', 'noone', 'ever', 'that', 'over', 'among', 'during', 'however', 'when', 'sometimes', 'still', 'seemed', 'get', "'ve", 'him', 'with', 'part', 'beyond', 'everyone', 'same', 'this', 'latterly', 'no', 'regarding', 'elsewhere', 'others', 'moreover', 'else', 'back', 'alone', 'somewhere', 'are', 'will', 'beforehand', 'ten', 'very', 'most', 'three', 'former', '’re', 'otherwise', 'several', 'also', 'whatever', 'am', 'becoming', 'beside', '’s', 'nothing', 'some', 'since', 'thence', 'anyway', 'out', 'up', 'well', 'it', 'various', 'four', 'top', '‘s', 'than', 'under', 'might', 'could', 'by', 'too', 'and', 'whom', '‘ll', 'say', 'therefore', "'s", 'other', 'throughout', 'became', 'your', 'put', 'per', "'ll", 'fifteen', 'must', 'before', 'whenever', 'anyone', 'without', 'does', 'was', 'where', 'thereafter', "'d", 'another', 'yourselves', 'n‘t', 'see', 'go', 'wherever', 'just', 'seeming', 'hence', 'full', 'whereafter', 'bottom', 'whole', 'own', 'empty', 'due', 'behind', 'while', 'onto', 'wherein', 'off', 'again', 'a', 'two', 'above', 'therein', 'sixty', 'those', 'whereas', 'using', 'latter', 'used', 'my', 'herself', 'hers', 'or', 'neither', 'forty', 'thereupon', 'now', 'after', 'yourself', 'whither', 'rather', 'once', 'from', 'until', 'anything', 'few', 'into', 'such', 'being', 'make', 'mine', 'please', 'along', 'hundred', 'should', 'below', 'third', 'unless', 'upon', 'perhaps', 'ours', 'but', 'never', 'whoever', 'fifty', 'any', 'all', 'nobody', 'there', 'have', 'anyhow', 'of', 'seem', 'down', 'is', 'every', '’ll', 'much', 'none', 'further', 'me', 'who', 'nevertheless', 'about', 'everywhere', 'name', 'enough', '’d', 'next', 'meanwhile', 'though', 'through', 'on', 'first', 'been', 'hereby', 'if', 'move', 'so', 'either', 'amongst', 'for', 'twelve', 'nor', 'she', 'always', 'these', 'as', '’ve', 'amount', '‘re', 'someone', 'afterwards', 'you', 'nowhere', 'itself', 'done', 'hereafter', 'within', 'made', 'ca', 'them'])
# print(type(STOP_WORDS))
STOP_WORDS.add("cite")

query = ""
# store = False
k = 10

weight = {
    "t": 100,
    "i": 20,
    "b": 1,
    "c": 20,
    "l": 0.05,
    "r": 0.05
}

first_words = ""    
# SORT_SIZE = 10000
TITLE_SIZE = 2000
N = 9829059
# queries_op = ""

def tokenize(data):
    return re.split(r"[^A-Za-z0-9]+", str(data))
    
def preprocess(data):
    return [stemmer.stemWord(token.casefold()) for token in tokenize(data) if token and token.casefold() not in STOP_WORDS]

def file_name(word):
    file_number = bisect.bisect_right(first_words, word)

    if file_number == 0:
        return ""
    
    return f"./inverted_index/{file_number - 1}.txt"

def postings(word):
    filename = file_name(word)

    if filename == "":
        return ""

    fp = open(filename, "r")
    cur = fp.readline().strip().strip("\n")

    while cur:
        temp = cur.split(":")
        
        if word == temp[0]:
            fp.close()
            return temp[1]

        cur = fp.readline().strip().strip("\n")
    
    fp.close()
    return ""

def title(doc_id):
    fp = open(f"./titles/{doc_id // TITLE_SIZE}.txt", "r")
    cur = fp.readline()
    
    line_id = doc_id % TITLE_SIZE
    cnt = 0
    
    while cnt < line_id:
        cur = fp.readline()
        cnt += 1

    return cur.strip()

fields = set(["t", "i", "b", "c", "l", "r"])

score = defaultdict(lambda: 0)

def process_normal_token(token):
    global score
    
    posting_list = postings(token)
    if posting_list == "":
        return

    df = posting_list.count("D")
    docs = posting_list.split("D")[1:]
    tf = 0
    idf = math.log10(N/df)
    w = 0
    num = ""
    
    for doc in docs:
        tf = 0
        doc_id = ""
        flag = False
        num = ""
        # print(doc)

        for ch in doc: 
            if ch in fields:
                if not flag:
                    flag = True
                    doc_id = int(doc_id)

                    num = ""
                    w = weight[ch]
                    # print(f"doc id is {doc_id} and weight is {w} for {ch}")
                    # print(ch, w)    

                else:
                    tf += w * int(num)
                    # if doc_id == 7882936:
                    #     print(token, w, int(num))
                    w = weight[ch]
                    num = ""
            
            else:
                if not flag:
                    doc_id += ch
                
                else:
                    num += ch
            
        tf += w * int(num)
        tf = math.log10(1 + tf)

        # if "Wikipedia:" not in title(doc_id):
        score[doc_id] += 10000
        score[doc_id] += tf * idf 

def process_field_token(token, field):
    global score

    posting_list = postings(token)

    if posting_list == "":
        return

    df = 0
    docs = posting_list.split("D")[1:]
    tf = 0
    w = 0
    num = ""

    for doc in docs:
        if field in doc:
            df += 1
        
        else:
            df += 0.2

    idf = math.log10(N/df)
    
    for doc in docs:
        tf = 0
        doc_id = ""
        flag = False
        num = ""

        for ch in doc: 
            if ch in fields:
                if not flag:
                    flag = True
                    doc_id = int(doc_id)
                    num = ""
                    w = weight[ch]
                    if ch == field:
                        w *= 10000

                else:
                    tf += w * int(num)
                    w = weight[ch]
                    if ch == field:
                        w *= 10000
                    num = ""
            
            else:
                if not flag:
                    doc_id += ch
                
                else:
                    num += ch
            
        tf += w * int(num)
        tf = math.log10(1 + tf)

        score[doc_id] += 10000
        score[doc_id] += tf * idf 

def plain_query(query):
    global score
    global queries_op

    tokens = preprocess(query)
    score = defaultdict(lambda: 0)

    for token in tokens:
        process_normal_token(token)    

    # print(score[8712373])
    
    ranks = sorted(score.items(), key = lambda x: x[1], reverse = True)

    length_ranks = len(ranks)

    for i in range(min(length_ranks, k)):
        queries_op += f"{ranks[i][0]}, {title(ranks[i][0]).lower()}\n"

    for i in range(max(0, k - length_ranks)):
        queries_op += f"{i}, {title(i).lower()}\n"

def field_query(query):
    global score
    global queries_op

    queries = query.split(":")
    length = len(queries)
    field = ""
    score = defaultdict(lambda: 0)

    # print(queries)

    for i, query in enumerate(queries):

        if i == length - 1:
            tokens = preprocess(query)

            for token in tokens:
                process_field_token(token, field)

            break

        if field.strip():
            new_field = query[-1]
            new_query = query[:-1]

            tokens = preprocess(new_query)

            for token in tokens:
                process_field_token(token, field)
            
            field = new_field

        else:
            field = query[-1]

            if len(query) > 1:
                new_query = query[:-1]

                tokens = preprocess(new_query)

                for token in tokens:
                    process_normal_token(token)

    ranks = sorted(score.items(), key = lambda x: x[1], reverse = True)

    length_ranks = len(ranks)

    for i in range(min(length_ranks, k)):
        queries_op += f"{ranks[i][0]}, {title(ranks[i][0]).lower()}\n"

    for i in range(max(0, k - length_ranks)):
        queries_op += f"{i}, {title(i).lower()}\n"

if __name__ == "__main__":
    # global queries_op

    queries_op = ""

    queries = sys.argv[1]

    fp = open("./inverted_index/bisect.txt", "r")
    first_words = fp.readlines()
    fp.close()

    with open(queries, "r") as fp:
        
        for line in fp:
            start = time.time()
            
            cur_query = line.split(",")
            k = int(cur_query[0])
            query = cur_query[1]

            if ":" in query:
                field_query(query)
            
            else:
                plain_query(query)
            
            end = time.time()

            queries_op += f"{round(end - start, 3)}, {round((end - start) / k, 3)}\n"
            # print(f"{end - start}, {(end - start) / k}")
            queries_op += "\n"
        
    with open("./queries_op.txt", "w") as fp:
        fp.write(queries_op)

