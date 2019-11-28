import os
import re
import sys
import numpy as np
from Orange.data import Domain, Table
from Orange.data import TimeVariable, ContinuousVariable, DiscreteVariable, StringVariable
from nltk import word_tokenize
from operator import itemgetter

N = 20
COMMAND = "LIWC"
EMPTYLIST = []
EMPTYSTRING = ""
FIELDNAMEFILE = "file"
FIELDNAMETEXT = "text"
FIELDNAMEEXTRA = "extra"
FIELDNAMEMSGID = "msg id"
LIWCFILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../widgets/Dicts' , 'LIWC-DO-NOT-DISTRIBUTE.txt')
TEXTBOUNDARY = "%"
NBROFTOKENS = "NBROFTOKENS"
NBROFMATCHES = "Number of matches"
MAXPREFIXLEN = 10
TOKENID = 0
LEMMAID = 1
NUMBER = "number"
SPACE = " "
SEPARATOR = " "
numberId = -1
NBROFDECIMALS = 5

def getFieldId(corpus,fieldName):
    fieldId = -1
    for i in range(0,len(corpus.domain.metas)):
        if str(corpus.domain.metas[i]) == fieldName:
            fieldId = i
    return(fieldId)

def prepareText(text):
    text = re.sub("</*line>", SPACE, text)
    text = re.sub(">>+", SPACE, text)
    return word_tokenize(text)

def isNumber(string):
    return string.lstrip("-").replace(".", "1").isnumeric()

def readEmpty(inFile):
    text = ""
    for line in inFile:
        line = line.strip()
        if line == TEXTBOUNDARY:
            break
        text += line + "\n"
    if text != "":
        sys.exit(COMMAND + ": liwc dictionary starts with unexpected text: " + text)

def readFeatures(inFile):
    featureNames = {}
    for line in inFile:
        line = line.strip()
        if line == TEXTBOUNDARY:
            break
        fields = line.split()
        featureId = fields.pop(0)
        featureName = SPACE.join(fields)
        featureNames[featureId] = featureName
        if featureName == NUMBER: numberId = featureId
    return(featureNames)

def makeUniqueElements(inList):
    outList = []
    seen = {}
    for element in inList:
        if not element in seen:
            outList.append(element)
            seen[element] = True
    return(outList)

def readWords(inFile):
    words = {}
    prefixes = {}
    for line in inFile:
        line = line.strip()
        if line == TEXTBOUNDARY: break
        fields = line.split()
        word = fields.pop(0).lower()
        word = re.sub(r"\*$", "", word)
        if re.search(r"-$", word):
            word = re.sub(r"-$", "", word)
            if not word in prefixes:
                prefixes[word] = fields
            else:
                words[word] = makeUniqueElements(words[word] + fields)
        else:
            if not word in words:
                words[word] = fields
            else:
                words[word] = makeUniqueElements(words[word] + fields)
    return(words, prefixes)

def readLiwc(inFileName):
    try:
        inFile = open(inFileName, "r")
    except Exception as e:
        sys.exit(COMMAND + ": cannot read LIWC dictionary " + inFileName)
    readEmpty(inFile)
    featureNames = readFeatures(inFile)
    words, prefixes = readWords(inFile)
    inFile.close()
    return(featureNames, words, prefixes)

def findLongestPrefix(prefixes, word):
    while not word in prefixes and len(word) > 0:
        chars = list(word)
        chars.pop(-1)
        word = "".join(chars)
    return(word)

def makeFeature(number,name):
    return(str(number)+SPACE+name)

def addFeatureToCounts(counts, feature, featureNames=None):
    key = feature
    if featureNames != None and feature in featureNames: 
        key = makeFeature(feature,featureNames[feature])
    if key in counts:
        counts[key] += 1
    else:
        counts[key] = 1

def text2liwc(words, prefixes, featureNames, tokens):
    counts = {}
    for word in tokens:
        if word in words:
            addFeatureToCounts(counts, NBROFMATCHES)
            for feature in words[word]:
                if feature.isdigit():
                    addFeatureToCounts(counts, feature, featureNames)
        longestPrefix = findLongestPrefix(prefixes, word)
        if longestPrefix != "":
            addFeatureToCounts(counts, NBROFMATCHES)
            for feature in prefixes[longestPrefix]:
                addFeatureToCounts(counts, feature, featureNames)
        if isNumber(word):
            addFeatureToCounts(counts, NBROFMATCHES)
            addFeatureToCounts(counts, "Number count")
    return(counts)

def liwcResults(text, words, prefixes, featureNames):
    tokens = prepareText(text)
    counts = text2liwc(words, prefixes, featureNames, tokens)
    return(counts)

def getColumnNames(thisList,featureNames):
    columnNames = []
    for row in thisList:
        for columnName in row:
            if not columnName in columnNames: columnNames.append(columnName)
    for feature in featureNames:
        featureName = makeFeature(feature,featureNames[feature])
        if not featureName in columnNames: columnNames.append(featureName)
    return(columnNames)

def list2table(thisList,featureNames):
    columnNames = getColumnNames(thisList,featureNames)
    table = []
    for row in thisList:
        table.append(row)
        for columnName in columnNames:
            if not columnName in row: table[-1][columnName] = '0'
    return(table,columnNames)

def keyCombine(number,string):
    if string == "": 
        if number > 0: return(str(number))
        else: return("")
    elif number > 0: return(str(number)+SEPARATOR+string)
    else: return(string)

def keySplit(key):
     keyParts = key.split(SEPARATOR)
     if len(keyParts) > 0 and re.match("^\d+$",keyParts[0]):
         number = keyParts.pop(0)
         return(int(number),SEPARATOR.join(keyParts))
     else:
         return(0,SEPARATOR.join(keyParts))

def sortKeys(keys):
    splitKeys = [keySplit(k) for k in keys]
    sortedKeys = sorted(splitKeys,key=itemgetter(0,1))
    return([keyCombine(k[0],k[1]) for k in sortedKeys])

def dataCombine(corpus,liwcResultList,featureNames):
    liwcResultTable,columnNames = list2table(liwcResultList,featureNames)
    fieldIdFile = getFieldId(corpus, FIELDNAMEFILE)
    domain = [ContinuousVariable(name=FIELDNAMEMSGID)]+list(corpus.domain.variables)
    for columnName in sortKeys(columnNames):
        domain.append(ContinuousVariable(name=columnName,number_of_decimals=NBROFDECIMALS))
    metas = [StringVariable(name="file")]
    dataOut = []
    metasOut = []
    for i in range(0,len(corpus)):
        fileName = corpus.metas[i][fieldIdFile]
        metasOut.append([fileName])
        row = [i+1]+list(corpus[i].values())
        for columnName in sortKeys(columnNames):
            if not re.match("^\d+$",columnName) or int(liwcResultTable[i][NBROFMATCHES]) == 0:
                row.append(int(liwcResultTable[i][columnName]))
            else:
                row.append(100.0*float(liwcResultTable[i][columnName])/float(liwcResultTable[i][NBROFMATCHES]))
        dataOut.append(row)
    table = Table.from_numpy(Domain(domain,metas=metas),np.array(dataOut),metas=np.array(metasOut))
    return(table) 

def processCorpus(corpus):
    fieldIdText = getFieldId(corpus, FIELDNAMETEXT)
    fieldIdExtra = getFieldId(corpus, FIELDNAMEEXTRA)
    featureNames, words, prefixes = readLiwc(LIWCFILE)
    liwcResultList = []
    for msgId in range(0, len(corpus.metas)):
        text = str(corpus.metas[msgId][fieldIdText])
        liwcResultList.append(liwcResults(text, words, prefixes, featureNames))
    liwcResultTable = dataCombine(corpus,liwcResultList,featureNames)
    return(liwcResultTable)
