import xml.sax
import sys
import re
import Stemmer
import json
import os

stemmer = Stemmer.Stemmer("english")

STOP_WORDS = set(['whence', 'here', 'show', 'were', 'why', 'n’t', 'the', 'whereupon', 'not', 'more', 'how', 'eight', 'indeed', 'i', 'only', 'via', 'nine', 're', 'themselves', 'almost', 'to', 'already', 'front', 'least', 'becomes', 'thereby', 'doing', 'her', 'together', 'be', 'often', 'then', 'quite', 'less', 'many', 'they', 'ourselves', 'take', 'its', 'yours', 'each', 'would', 'may', 'namely', 'do', 'whose', 'whether', 'side', 'both', 'what', 'between', 'toward', 'our', 'whereby', "'m", 'formerly', 'myself', 'had', 'really', 'call', 'keep', "'re", 'hereupon', 'can', 'their', 'eleven', '’m', 'even', 'around', 'twenty', 'mostly', 'did', 'at', 'an', 'seems', 'serious', 'against', "n't", 'except', 'has', 'five', 'he', 'last', '‘ve', 'because', 'we', 'himself', 'yet', 'something', 'somehow', '‘m', 'towards', 'his', 'six', 'anywhere', 'us', '‘d', 'thru', 'thus', 'which', 'everything', 'become', 'herein', 'one', 'in', 'although', 'sometime', 'give', 'cannot', 'besides', 'across', 'noone', 'ever', 'that', 'over', 'among', 'during', 'however', 'when', 'sometimes', 'still', 'seemed', 'get', "'ve", 'him', 'with', 'part', 'beyond', 'everyone', 'same', 'this', 'latterly', 'no', 'regarding', 'elsewhere', 'others', 'moreover', 'else', 'back', 'alone', 'somewhere', 'are', 'will', 'beforehand', 'ten', 'very', 'most', 'three', 'former', '’re', 'otherwise', 'several', 'also', 'whatever', 'am', 'becoming', 'beside', '’s', 'nothing', 'some', 'since', 'thence', 'anyway', 'out', 'up', 'well', 'it', 'various', 'four', 'top', '‘s', 'than', 'under', 'might', 'could', 'by', 'too', 'and', 'whom', '‘ll', 'say', 'therefore', "'s", 'other', 'throughout', 'became', 'your', 'put', 'per', "'ll", 'fifteen', 'must', 'before', 'whenever', 'anyone', 'without', 'does', 'was', 'where', 'thereafter', "'d", 'another', 'yourselves', 'n‘t', 'see', 'go', 'wherever', 'just', 'seeming', 'hence', 'full', 'whereafter', 'bottom', 'whole', 'own', 'empty', 'due', 'behind', 'while', 'onto', 'wherein', 'off', 'again', 'a', 'two', 'above', 'therein', 'sixty', 'those', 'whereas', 'using', 'latter', 'used', 'my', 'herself', 'hers', 'or', 'neither', 'forty', 'thereupon', 'now', 'after', 'yourself', 'whither', 'rather', 'once', 'from', 'until', 'anything', 'few', 'into', 'such', 'being', 'make', 'mine', 'please', 'along', 'hundred', 'should', 'below', 'third', 'unless', 'upon', 'perhaps', 'ours', 'but', 'never', 'whoever', 'fifty', 'any', 'all', 'nobody', 'there', 'have', 'anyhow', 'of', 'seem', 'down', 'is', 'every', '’ll', 'much', 'none', 'further', 'me', 'who', 'nevertheless', 'about', 'everywhere', 'name', 'enough', '’d', 'next', 'meanwhile', 'though', 'through', 'on', 'first', 'been', 'hereby', 'if', 'move', 'so', 'either', 'amongst', 'for', 'twelve', 'nor', 'she', 'always', 'these', 'as', '’ve', 'amount', '‘re', 'someone', 'afterwards', 'you', 'nowhere', 'itself', 'done', 'hereafter', 'within', 'made', 'ca', 'them'])
# print(type(STOP_WORDS))
STOP_WORDS.add("cite")
# STOP_WORDS.add("redirect")

inverted_index = {}
doc_index = {}
doc_id = 0
stat_tokens = 0

def postings():
    
    data = sorted(doc_index.keys())

    for token in data:
        if token not in inverted_index:
            inverted_index[token] = ""
        
        counts = doc_index[token]

        field = f"D{doc_id}"
        prefixes = ["t", "i", "b", "c", "l", "r"]
        for i in range(6):
            if counts[i] > 0:
                field += f"{prefixes[i]}{counts[i]}"

        inverted_index[token] += field


# [title, infobox, body, category, links, references]
def indexer(data, ind):
    
    if ind == 2:
        length = len(data)
        if (length > 0 and data[0] == "redirect") or (length > 1 and data[1] == "redirect"):
            # print(doc_id, "REDIRECT MATCHED!!!")
            return

    for token in data:
        if token not in doc_index:
            doc_index[token] = [0, 0, 0, 0, 0, 0]
        
        doc_index[token][ind] += 1

def tokenize(data):
    global stat_tokens

    data = re.split(r"[^A-Za-z0-9]+", data)
    stat_tokens += len(data)

    return data

def preprocess(data):
    return [stemmer.stemWord(token.casefold()) for token in tokenize(data) if token and token.casefold() not in STOP_WORDS]

def parse_infobox(body):
    infoboxes = re.findall(r"\{\{Infobox (.*?)\}\}[\r\n]", str(body), flags=re.DOTALL)
    body = re.sub(r"\{\{Infobox (.*?)\}\}[\r\n]", "", str(body), flags=re.DOTALL)

    for infobox in infoboxes:
        indexer(preprocess(infobox), 1)
    
    return body

def parse_categories(body):
    categories = re.findall(r"\[\[Category:(.*)\]\]", str(body), flags=re.DOTALL)
    body = re.sub(r"\[\[Category:(.*)\]\]", "", str(body), flags=re.DOTALL)

    for category in categories:
        indexer(preprocess(category), 3)

    return body

def parse_links(body):
    data = body.split("==External links==")

    if len(data) <= 1:
        data = body.split("==External links ==")
    
        if len(data) <= 1:
            data = body.split("== External links ==")

            if len(data) <= 1:
                data = body.split("== External links==")
            
                if len(data) <= 1:
                    data = body.split("==External Links==")
                
                    if len(data) <= 1:
                        data = body.split("==External Links ==")
                    
                        if len(data) <= 1:
                            data = body.split("== External Links ==")
                        
                            if len(data) <= 1:
                                data = body.split("== External Links==")

    if len(data) <= 1:
        return body

    links = [link for link in data[1].split("\n") if link and link[0] == "*"]

    for link in links:
        indexer(preprocess(link), 4)

    return data[0]

def parse_references(body):

    # data = body.split("==References==")

    # if len(data) <= 1:
    #     data = body.split("==References ==")
    
    #     if len(data) <= 1:
    #         data = body.split("== References ==")

    #         if len(data) <= 1:
    #             data = body.split("== References==")
    
    # data = data[0]

    data = body
            
    references = re.findall(r"<ref[^/]*?>(.*?)</ref>", str(data), flags=re.DOTALL)
    data = re.sub(r"<ref[^/]*?>(.*?)</ref>", "", str(data), flags=re.DOTALL)

    for reference in references:
        indexer(preprocess(reference), 5)

    return data


class WikiHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.tag = ""
        self.title = ""
        self.body = ""
        self.infoboxes = []
        self.categories = []
        self.links = []
        self.current = ""
        
    def startElement(self, tag, attributes):
        self.tag = tag
        self.current = ""
    
    def endElement(self, tag):
        global doc_id
        global doc_index

        if tag == "title":
            self.title = self.current
        
        elif tag == "text":
            self.body = self.current

        elif tag == "page":
            self.body = parse_infobox(self.body)
            self.body = parse_categories(self.body)
            self.body = parse_links(self.body)
            self.body = parse_references(self.body)

            indexer(preprocess(self.title), 0)
            indexer(preprocess(self.body), 2)

            # print(self.title)
            # print(stat_tokens)

            postings()

            
            self.tag = ""
            self.title = ""
            self.body = ""
            self.infoboxes = []
            self.categories = []
            self.links = []
            doc_id += 1
            doc_index = {}

    def characters(self, content):
        self.current += content

def parse(data):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = WikiHandler()
    parser.setContentHandler(Handler)
    parser.parse(data)

if __name__ == "__main__":
    f = sys.argv[1]
    parse(f)

    if not os.path.exists(sys.argv[2]):
        os.makedirs(sys.argv[2])

    with open(f"{sys.argv[2]}/inverted_index.json", "w") as fp:
        json.dump(inverted_index, fp)

    f = open(sys.argv[3], "w")
    f.write(f"{stat_tokens}\n{len(inverted_index.keys())}\n")
    f.close()