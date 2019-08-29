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
import datetime
import numpy as np

class MarkDuplicates(OWWidget):
    name = "Mark Duplicates"
    description = "Mark duplicate text parts in corpus"
    icon = "icons/MarkDuplicates.svg"
    N = 20
    EMPTYLIST = []
    EMPTYSTRING = ""
    FIELDNAMEDATE = "date"
    FIELDNAMETEXT = "text"
    FIELDNAMEEXTRA = "extra"
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
        # self.label.setText(str(duplicateRefStartEnds))
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

    def getFieldId(self,corpus,fieldName):
        fieldId = -1
        for i in range(0,len(corpus.domain.metas)):
            if str(corpus.domain.metas[i]) == fieldName:
                fieldId = i
        return(fieldId)

    @Inputs.corpus
    def inputAnalysis(self, corpus):
        self.resetWidget()
        self.corpus = corpus
        OWWidget.progressBarInit(self)
        duplicateRefStartEndsArray = list(self.EMPTYLIST)
        if self.corpus is None:
            self.label.setText("No corpus available")
        else:
            text = self.EMPTYSTRING
            self.fieldIdDate = self.getFieldId(self.corpus,self.FIELDNAMEDATE)
            self.fieldIdText = self.getFieldId(self.corpus,self.FIELDNAMETEXT)
            self.fieldIdExtra = self.getFieldId(self.corpus,self.FIELDNAMEEXTRA)
            for msgId in range(0,len(self.corpus.metas)):
                date = datetime.datetime.fromtimestamp(self.corpus.metas[msgId][self.fieldIdDate],tz=datetime.timezone.utc)
                text = self.prepareText(str(self.corpus.metas[msgId][self.fieldIdText]))
                duplicateRefStartEnds = self.countPhrases(date,text,msgId)
                duplicateRefStartEndsArray.append([list(duplicateRefStartEnds)])
                self.label.setText(str(duplicateRefStartEnds))
                self.corpus.metas[msgId][self.fieldIdExtra] = list(duplicateRefStartEnds)
                self.corpus.metas[msgId][self.fieldIdText] = self.markDuplicates(text,duplicateRefStartEnds)
                OWWidget.progressBarSet(self,100*(msgId+1)/len(self.corpus.metas))
        # np.append(self.corpus.metas,np.array(duplicateRefStartEndsArray),axis=1) 
        self.Outputs.corpus.send(self.corpus)
