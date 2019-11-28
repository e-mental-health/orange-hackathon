import re
import sys

N = 20
COMMAND = "removemarkedtext"
EMPTYSTRING = ""
FIELDNAMETEXT = "text"
corpus = None
phraseRefs = {}

def getFieldValue(corpus,fieldName,rowId):
    for i in range(0,len(corpus.domain)):
        if corpus.domain[i].name == fieldName:
            return(corpus[rowId].list[i])
    for i in range(0,len(corpus.domain.metas)):
        if corpus.domain.metas[i].name == fieldName:
            return(corpus[rowId].metas[i])
    sys.exit("getFieldValue: field name not found: "+fieldName)

def setFieldValue(corpus,fieldName,rowId,value):
    for i in range(0,len(corpus.domain)):
        if corpus.domain[i].name == fieldName:
            # 20190830 assignment does not work: imutable object?
            corpus[rowId].list[i] = value
            return
    for i in range(0,len(corpus.domain.metas)):
        if corpus.domain.metas[i].name == fieldName:
            corpus[rowId].metas[i] = value
            return
    sys.exit("setFieldValue: field name not found: "+fieldName)

def processText(text):
    text = re.sub("<mark[^<>]*>[^<>]*</mark>"," ",text)
    text = re.sub("</*text>"," ",text)
    checkText(text)
    text = re.sub("&lt;","<",text)
    text = re.sub("&gt;",">",text)
    text = re.sub("  *"," ",text)
    return(text)

def checkText(text):
    if re.search("[<>]",text): 
        print(COMMAND+": found unexpected < or > in text: "+text,file=sys.stderr)

def processCorpus(corpus):
    for msgId in range(0,len(corpus)):
        textFieldValue = getFieldValue(corpus,FIELDNAMETEXT,msgId)
        processedText = processText(textFieldValue)
        setFieldValue(corpus,FIELDNAMETEXT,msgId,processedText)
    return(corpus)
