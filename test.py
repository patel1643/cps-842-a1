import collections
import re
from typing import OrderedDict
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import json

corpusFile = './trec_corpus_20220301_plain.json'



def lineParserPostings(s: str) -> dict:
    postings = []
    count = 0

    firstSplit = s.split(':', 1)
    term = firstSplit[0]

    #splits all the different occurances in different documents
    postingsSplit = firstSplit[1].split('|')

    #Removes the last empty list with the split
    postingsSplit.pop()
    
    for posting in postingsSplit:
        firstPostingSplit = posting.split('=')
        listStr = firstPostingSplit[3]
        listStr = listStr[1:-1]
        positionsList = listStr.split(', ')
        postingsListInt = list(map(int, positionsList))
        tempPostingObj = {
            'frequency': firstPostingSplit[2],
            'title': firstPostingSplit[1],
            'docId': firstPostingSplit[0],
            'positions': postingsListInt
        }
        postings.append(tempPostingObj)
    return { term : postings }

def lineParserDict(s: str) -> dict:
    splitList = re.split(r'\t+', s)
    return { splitList[0] : splitList[1]}


def search(query: str, dict: dict, postings: dict, corpus:dict):
    rtrValue = None
    if query in dict:
        rtrValues = postings.get(query)
        for rtrValue in rtrValues:
            sampleStr = ''
            firstPos = int(rtrValue['positions'][0])
            tempDocId = rtrValue['docId'] 
            sample = corpus.get(int(tempDocId))
            sample = word_tokenize(sample)
            sampleLength = len(sample)
            if (firstPos < 10):
                count = 0
                while True:
                    if(count == 10):
                        break
                    sampleStr += sample[firstPos]+ " "
                    firstPos+=1
                    count+=1
            elif(firstPos+10 > sampleLength-1):
                firstPos = firstPos-10
                count = 0
                while True:
                    if(count == 10):
                        break
                    sampleStr += sample[firstPos]+ " "
                    firstPos+=1
                    count+=1
            else:
                firstPos = firstPos - 5
                count = 0
                while True:
                    if(count == 10):
                        break
                    sampleStr += sample[firstPos] + " "
                    firstPos+=1
                    count+=1
            rtrValue['sample'] = sampleStr
    else:
        rtrValues = "No matches found, please try again!"
    return rtrValues

def readData():
    data = collections.OrderedDict()
    count = 0
    with open(corpusFile, 'r') as file:
        for line in file:
            count += 1
            json_line = json.loads(line)
            data[json_line['id']] = json_line['plain']
            if count > 20000:
                break
    return data


def mainSearchProgram():
    dictionary = collections.OrderedDict()
    postings = collections.OrderedDict()
    
    print('Please wait while we load the postings file...')
    with open('PostingList.txt', 'r') as file:
        while (line := file.readline().rstrip()):
            postingPair = lineParserPostings(line)
            postings[list(postingPair.keys())[0]] = postingPair[list(postingPair.keys())[0]]

    print('Please wait while we load the dictionary file...')
    with open('Dictionary.txt', 'r') as file:
        while (line := file.readline().rstrip()):
            dictionaryPair = lineParserDict(line)
            dictionary[list(dictionaryPair.keys())[0]] = dictionaryPair[list(dictionaryPair.keys())[0]]

    print('Please wait while we load the corpus file...')
    corpus = collections.OrderedDict(readData())

    while True:
        results = None
        query = str(input('\nPlease search here... \n'))
        if (query == 'ZZEND'):
            print('END OF SEARCH PROGRAM!')
            break
        else:
            query = query.lower()
            #Submit the query to the search function and store the result it in a variable
            results = search(query, dictionary, postings, corpus)
            print(results)

mainSearchProgram()