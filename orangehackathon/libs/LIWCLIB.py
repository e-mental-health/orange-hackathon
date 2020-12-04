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
FIELDNAMECOUNSELOR = "counselor"
FIELDNAMETEXT = "text"
FIELDNAMEEXTRA = "extra"
FIELDNAMEMSGID = "msg id"
FIELDNAMEMARKEDTEXT = "markedtext"
LIWCFILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../widgets/Dicts' , 'LIWC-DO-NOT-DISTRIBUTE.txt')
TEXTBOUNDARY = "%"
NBROFTOKENS = "NBROFTOKENS"
NBROFMATCHES = "Number of matches"
NUMBERCOUNT = "number count"
MAXPREFIXLEN = 10
TOKENID = 0
LEMMAID = 1
NUMBER = "number"
SPACE = " "
SEPARATOR = SPACE
numberId = -1
NBROFDECIMALS = 5
MARKERTOKEN = "@"
NUM = "NUM"
EXCEPTIONLIST = ["DATE","EVE","LOC","MISC","NUM","ORG","PER","PRO"]

def getFieldId(corpus,fieldName):
    fieldId = -1
    for i in range(0,len(corpus.domain.metas)):
        if str(corpus.domain.metas[i]) == fieldName:
            fieldId = i
    return(fieldId)

def toLower(wordList):
    loweredList = []
    for word in wordList:
        if word in EXCEPTIONLIST: loweredList.append(word)
        else: loweredList.append(word.lower())
    return(loweredList)

def prepareText(text):
    text = re.sub("</*line>", SPACE, text)
    text = re.sub(">>+", SPACE, text)
    return(toLower(word_tokenize(text)))

def isNumber(string):
    if string == NUM: return(True)
    try:
        float(string)
        return(True)
    except ValueError:
        return(False)

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
    markedTokens = []
    for word in tokens:
        markedTokens.append(word)
        if word in words:
            addFeatureToCounts(counts, NBROFMATCHES)
            for feature in words[word]:
                if feature.isdigit():
                    addFeatureToCounts(counts, feature, featureNames)
                    markedTokens[-1] += MARKERTOKEN+featureNames[feature]
        longestPrefix = findLongestPrefix(prefixes, word)
        if longestPrefix != "":
            addFeatureToCounts(counts, NBROFMATCHES)
            for feature in prefixes[longestPrefix]:
                addFeatureToCounts(counts, feature, featureNames)
                markedTokens[-1] += MARKERTOKEN+featureNames[feature]
        if isNumber(word):
            addFeatureToCounts(counts, NBROFMATCHES)
            addFeatureToCounts(counts, NUMBERCOUNT)
            markedTokens[-1] += MARKERTOKEN+NUMBERCOUNT
    return(counts,SPACE.join(markedTokens))

def liwcResults(text, words, prefixes, featureNames):
    tokens = prepareText(text)
    counts,markedText = text2liwc(words, prefixes, featureNames, tokens)
    return(counts,markedText)

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

def dataCombine(corpus,liwcResultList,featureNames,markedTexts):
    liwcResultTable,columnNames = list2table(liwcResultList,featureNames)
    fieldIdFile = getFieldId(corpus, FIELDNAMEFILE)
    fieldIdCounselor = getFieldId(corpus, FIELDNAMECOUNSELOR)
    domain = [ContinuousVariable(name=FIELDNAMEMSGID)]+list(corpus.domain.variables)
    for columnName in sortKeys(columnNames):
        domain.append(ContinuousVariable(name=columnName,number_of_decimals=NBROFDECIMALS))
    metas = [StringVariable(name=FIELDNAMEFILE),StringVariable(name=FIELDNAMECOUNSELOR),StringVariable(name=FIELDNAMEMARKEDTEXT)]
    dataOut = []
    metasOut = []
    for i in range(0,len(corpus)):
        fileName = corpus.metas[i][fieldIdFile]
        counselorId = corpus.metas[i][fieldIdCounselor]
        metasOut.append([fileName,counselorId,markedTexts[i]])
        row = [i+1]+list(corpus[i].values())
        for columnName in sortKeys(columnNames):
            if (not re.match("^\d+\s",columnName) and columnName != NUMBERCOUNT) or int(liwcResultTable[i][NBROFMATCHES]) == 0:
                row.append(int(liwcResultTable[i][columnName]))
            else:
                row.append(float(liwcResultTable[i][columnName])/float(liwcResultTable[i][NBROFMATCHES]))
        dataOut.append(row)
    table = Table.from_numpy(Domain(domain,metas=metas),np.array(dataOut),metas=np.array(metasOut))
    return(table) 

def processCorpus(corpus,windowId=None):
    if len(corpus) == 0: return(corpus)
    fieldIdText = getFieldId(corpus, FIELDNAMETEXT)
    fieldIdExtra = getFieldId(corpus, FIELDNAMEEXTRA)
    featureNames, words, prefixes = readLiwc(LIWCFILE)
    liwcResultList = []
    markedTexts = []
    # if progress != None: progress.iter = len(corpus.metas)
    for msgId in range(0, len(corpus.metas)):
        text = str(corpus.metas[msgId][fieldIdText])
        counts,markedText = liwcResults(text, words, prefixes, featureNames)
        liwcResultList.append(counts)
        markedTexts.append(markedText)
        if windowId != None: windowId.progressBarSet(100*(msgId+1)/len(corpus.metas))
    liwcResultTable = dataCombine(corpus,liwcResultList,featureNames,markedTexts)
    return(liwcResultTable)
