#!/usr/bin/env python
# mark-duplicates.py: mark duplicate text in email text
# usage: mark-duplicates.py (in orange3 environment)
# note: assumes input corpus is sorted by date
# 20190726 erikt(at)xs4all.nl

from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui
from orangecontrib.text.corpus import Corpus
from Orange.data.domain import filter_visible
from itertools import chain
from nltk import word_tokenize
import re
import sys
import datetime
import numpy as np

class MarkDuplicates(OWWidget):
    name = "Mark Duplicates"
    description = "Mark duplicate text parts in corpus"
    icon = "icons/globe.svg"
    N = 20
    EMPTYLIST = []
    EMPTYSTRING = ""
    FIELDNAMEDATE = "date"
    FIELDNAMETEXT = "text"
    FIELDNAMECOORDINATES = "coordinates"
    DATEFORMAT = "%Y-%m-%d %H:%M:%S"
    want_main_area = False

    class Inputs:
        corpus = Input("Corpus", Corpus)

    class Outputs:
        corpus = Output("Corpus", Corpus)

    def resetWidget(self):
        self.corpus = None
        self.phraseRefs = {}

    def __init__(self):
        super().__init__()
        self.label = gui.widgetLabel(self.controlArea)
        self.progress = gui.ProgressBar(self, 100)
        self.resetWidget()
    
    def makeRefId(self,msgId,index):
        return(" ".join([str(msgId+1),str(index)]))

    def getDateFromRefId(self,refId):
        return(" ".join(refId.split()[0:2]))
    
    def makePhrase(self,wordList,index):
        return(" ".join(wordList[index:index+self.N]))

    def addPhraseToRefs(self,phrase,msgId,index):
        self.phraseRefs[phrase] = self.makeRefId(msgId,index)

    def getMsgIdFromRef(self,ref):
        return(ref.split()[0])

    def countPhrases(self,date,message,msgId):
        words = message.split()
        inDuplicate = False
        duplicateRefStartEnds = list(self.EMPTYLIST)
        for i in range(0,len(words)-self.N+1):
            phrase = self.makePhrase(words,i)
            if not phrase in self.phraseRefs:
                self.addPhraseToRefs(phrase,msgId,i)
                if inDuplicate: inDuplicate = False
            else:
                if inDuplicate and \
                   self.getMsgIdFromRef(duplicateRefStartEnds[-1][0]) == \
                       self.getMsgIdFromRef(self.phraseRefs[phrase]) and \
                   duplicateRefStartEnds[-1][-1] == i+self.N-1:
                    duplicateRefStartEnds[-1][-1] += 1
                else:
                    inDuplicate = True
                    duplicateSource = self.phraseRefs[phrase]
                    duplicateStart = i
                    duplicateEnd = i+self.N
                    duplicateRefStartEnds.append([duplicateSource,duplicateStart,duplicateEnd])
        return(duplicateRefStartEnds)

    def markDuplicates(self,message,duplicateRefStartEnds):
        words = message.split()
        outText = self.EMPTYSTRING
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

    def prepareText(self,text):
        text = re.sub("</*line>"," ",text)
        text = re.sub(">>+"," ",text)
        text = " ".join(word_tokenize(text))
        return(text)

    def getFieldValue(self,corpus,fieldName,rowId):
        for i in range(0,len(corpus.domain)):
            if corpus.domain[i].name == fieldName:
                return(corpus[rowId].list[i])
        for i in range(0,len(corpus.domain.metas)):
            if corpus.domain.metas[i].name == fieldName:
                return(corpus[rowId].metas[i])
        sys.exit("getFieldValue: field name not found: "+fieldName)

    def setFieldValue(self,corpus,fieldName,rowId,value):
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

    @Inputs.corpus
    def inputAnalysis(self, corpus):
        self.resetWidget()
        self.corpus = corpus
        OWWidget.progressBarInit(self)
        if self.corpus is None:
            self.label.setText("No corpus available")
        else:
            self.label.setText("Processing corpus")
            text = self.EMPTYSTRING
            coordinatesList = []
            for msgId in range(0,len(self.corpus)):
                dateFieldValue = self.getFieldValue(corpus,self.FIELDNAMEDATE,msgId)
                textFieldValue = self.getFieldValue(corpus,self.FIELDNAMETEXT,msgId)
                date = datetime.datetime.fromtimestamp(dateFieldValue,tz=datetime.timezone.utc)
                text = self.prepareText(textFieldValue)
                duplicateRefStartEnds = self.countPhrases(date,text,msgId)
                coordinatesList.append(str(duplicateRefStartEnds))
                markedText = self.markDuplicates(text,duplicateRefStartEnds)
                self.setFieldValue(corpus,self.FIELDNAMETEXT,msgId,markedText)
                OWWidget.progressBarSet(self,100*(msgId+1)/len(self.corpus))
#           self.corpus.extend_corpus(np.array(coordinatesList),np.array([self.FIELDNAMECOORDINATES]))
        self.Outputs.corpus.send(self.corpus)
