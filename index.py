import json
import sys
import logging
from collections import OrderedDict
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import collections
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import PorterStemmer


logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger('Inverted Index Logger')
ps = PorterStemmer()
filePath = 'trec_corpus_20220301_plain.json';
# filePath = 'test.json'

class InvertedIndex:
    def __init__(self):
        self.index = OrderedDict()

    def add(self, data):
        doc_id = data['id']
        title = data['title']
        plain_text = data['plain']
        tokenized_text = self.parse_text(plain_text)

        for i in range(len(tokenized_text)):
            text_lower = tokenized_text[i].lower()
            if text_lower not in self.index:
                self.index[text_lower] = [{ 'frequency' : 1, 'title':title, 'docId' : doc_id , 'positions': [i] }]
            else:
                last_doc_id = self.index[text_lower][len(self.index[text_lower])-1]['docId']
                if doc_id == last_doc_id:
                    curr_posting = self.index[text_lower][len(self.index[text_lower])-1]
                    curr_posting['frequency'] += 1
                    curr_posting['positions'].append(i)
                else:
                    self.index[text_lower].append({ 'frequency' : 1, 'title':title, 'docId' : doc_id , 'positions': [i] });

        
    def sort(self):
        self.index = collections.OrderedDict(sorted(self.index.items()))

    
    def parse_text(self, text):
        tokenized_text = word_tokenize(text);
        if "-s" in sys.argv:
            tokenized_text = [ word for word in tokenized_text if not word in stopwords.words('english')]
        if "-p" in sys.argv:
            tokenized_text = [ ps.stem(word) for word in tokenized_text]

        return tokenized_text
        
    
        
        



def readData():
    logger.info('Reading Raw Data From JSON')
    data = [json.loads(line) for line in open(filePath, 'r', encoding='utf-8')]
    logger.info('Done reading Raw Data')
    return data

def initIndex(data):
    logger.info("Initializing Index...")
    index = InvertedIndex()

    for row in data:
        index.add(row)
    
    index.sort()

    logger.info("Index Initialized")

    return index

def getDocFreqDict(inputDict):
    newDict = OrderedDict()
    for key in inputDict.keys():
        docFreq = len(inputDict[key])
        newDict[key] = docFreq
    return newDict

def writeDictToFile(dict, fileName):
    with open(fileName, 'w') as f: 
        for key, value in dict.items(): 
            f.write('%s\t%s\n' % (key, value))

def writeIndexDictToFile(dict, fileName):
    with open(fileName, 'w') as f: 
        for key, value in dict.items(): 
            f.write('%s:' % (key))
            for posting in value:
                f.write('%s=%s=%s=%s|' % (posting['docId'],posting['title'],posting['frequency'],posting['positions']))
            f.write('\n')

if "-s" in sys.argv:
    logger.info("Stop Words Flag Activated: Stop Words Will Be Removed")
if "-p" in sys.argv:
    logger.info("Porter Stemming Flag Activated: Terms Will Be Stemmed")

      
data = readData()
index = initIndex(data)
docFreqDict = getDocFreqDict(index.index)
writeIndexDictToFile(index.index, "PostingList.txt")
writeDictToFile(docFreqDict, "Dictionary.txt")
