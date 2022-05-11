from orangecontrib.text.corpus import Corpus
from nltk import word_tokenize
import re
import sys
import datetime
from Orange.data import Table, Domain
from Orange.data import StringVariable

N = 20
EMPTYLIST = []
EMPTYSTRING = ""
FIELDNAMEDATE = "date"
FIELDNAMETEXT = "text"
FIELDNAMECOORDINATES = "coordinates"
COLUMNDOMAIN = StringVariable.make(FIELDNAMECOORDINATES)

def makeRefId(msgId,index):
    return(" ".join([str(msgId+1),str(index)]))

def getDateFromRefId(refId):
    return(" ".join(refId.split()[0:2]))

def makePhrase(wordList,index):
    return(" ".join(wordList[index:index+N]))

def addPhraseToRefs(phraseRefs,phrase,msgId,index):
    phraseRefs[phrase] = makeRefId(msgId,index)

def getMsgIdFromRef(ref):
    return(ref.split()[0])

def countPhrases(phraseRefs,date,message,msgId):
    words = message.split()
    inDuplicate = False
    duplicateRefStartEnds = list(EMPTYLIST)
    for i in range(0,len(words)-N+1):
        phrase = makePhrase(words,i)
        if not phrase in phraseRefs:
            addPhraseToRefs(phraseRefs,phrase,msgId,i)
            if inDuplicate: inDuplicate = False
        else:
            if inDuplicate and \
               getMsgIdFromRef(duplicateRefStartEnds[-1][0]) == \
                   getMsgIdFromRef(phraseRefs[phrase]) and \
               duplicateRefStartEnds[-1][-1] == i+N-1:
                duplicateRefStartEnds[-1][-1] += 1
            else:
                inDuplicate = True
                duplicateSource = phraseRefs[phrase]
                duplicateStart = i
                duplicateEnd = i+N
                duplicateRefStartEnds.append([duplicateSource,duplicateStart,duplicateEnd])
    return(duplicateRefStartEnds)

def escapeXml(text):
    text = re.sub("<","&lt;",text)
    text = re.sub(">","&gt;",text)
    return(text)

def markDuplicates(message,duplicateRefStartEnds):
    words = escapeXml(message).split()
    outText = EMPTYSTRING
    wordIndex = 0
    while len(duplicateRefStartEnds) > 0:
        duplicateSource,duplicateStart,duplicateEnd = duplicateRefStartEnds.pop(0)
        if duplicateStart > wordIndex:
            outText += "<text>"+" ".join(words[wordIndex:duplicateStart])+"</text>"
        if duplicateStart < duplicateEnd:
            maxIndex = max(duplicateStart,wordIndex)
            outText += '<mark data-markjs="true">'+" ".join(words[maxIndex:duplicateEnd])+"</mark>"
        wordIndex = duplicateEnd
    if wordIndex < len(words):
        outText += "<text>"+" ".join(words[wordIndex:])+"</text>"
    return(outText)

def prepareText(text):
    text = re.sub("</*line>"," ",text)
    text = re.sub(">>+"," ",text)
    text = " ".join(word_tokenize(text))
    return(text)

def getFieldValue(corpus,fieldName,rowId):
    for i in range(0,len(corpus.domain.variables)):
        if corpus.domain[i].name == fieldName:
            return(corpus[rowId].list[i])
    for i in range(0,len(corpus.domain.metas)):
        if corpus.domain.metas[i].name == fieldName:
            return(corpus[rowId].metas[i])
    sys.exit("getFieldValue: field name not found: "+fieldName)

def setFieldValue(corpus,fieldName,rowId,value):
    for i in range(0,len(corpus.domain.variables)):
        if corpus.domain[i].name == fieldName:
            # 20190830 assignment does not work: imutable object?
            corpus[rowId].list[i] = value
            return
    for i in range(0,len(corpus.domain.metas)):
        if corpus.domain.metas[i].name == fieldName:
            corpus[rowId].metas[i] = value
            return
    sys.exit("setFieldValue: field name not found: "+fieldName)

def addMetaDomain(corpusDomain,columnDomain):
    metas = list(corpusDomain.metas)
    metas.append(columnDomain)
    return(Domain(corpusDomain.attributes,metas=metas))

def addMetaData(corpus,columnData):
    return([corpus[i].list+[columnData[i]] for i in range(0,len(corpus))])

def addMetaDataColumn(corpus,columnData,columnDomain):
    newDomain = addMetaDomain(corpus.domain,columnDomain)
    newArray = addMetaData(corpus,columnData)
    newTable = Table.from_list(newDomain,newArray)
    newCorpus = Corpus.from_table(newDomain,newTable)
    return(newCorpus)

def processCorpus(corpus,windowId=None):
    phraseRefs = {}
    coordinatesList = []
    for msgId in range(0,len(corpus)):
        dateFieldValue = getFieldValue(corpus,FIELDNAMEDATE,msgId)
        textFieldValue = getFieldValue(corpus,FIELDNAMETEXT,msgId)
        date = datetime.datetime.fromtimestamp(dateFieldValue,tz=datetime.timezone.utc)
        text = prepareText(textFieldValue)
        duplicateRefStartEnds = countPhrases(phraseRefs,date,text,msgId)
        coordinatesList.append(str(duplicateRefStartEnds))
        markedText = markDuplicates(text,duplicateRefStartEnds)
        setFieldValue(corpus,FIELDNAMETEXT,msgId,markedText)
        if windowId != None: windowId.progressBarSet(100*(msgId+1)/len(corpus))
    if len(corpus) > 0: corpus = addMetaDataColumn(corpus,coordinatesList,COLUMNDOMAIN)
    return(corpus)
