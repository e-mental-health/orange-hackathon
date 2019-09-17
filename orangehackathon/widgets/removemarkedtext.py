#!/usr/bin/env python
# removemarkedtext.py: remove marked text
# usage: removemarkedtext.py (in orange3 environment)
# note: removes text between tags <mark>...</mark>
# 20190917 erikt(at)xs4all.nl

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
from Orange.data import Table, Domain
from Orange.data import StringVariable

class MarkDuplicates(OWWidget):
    name = "Remove Marked Text"
    description = "Remove marked text from corpus"
    icon = "icons/default.svg"
    N = 20
    EMPTYSTRING = ""
    FIELDNAMETEXT = "text"
    # want_main_area = False

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

    def processText(self,text):
        text = re.sub("<mark[^<>]*>[^<>]*</mark>"," ",text)
        text = re.sub("</*text>"," ",text)
        self.checkText(text)
        text = re.sub("&lt;","<",text)
        text = re.sub("&gt;",">",text)
        text = re.sub("  *"," ",text)
        return(text)

    def checkText(self,text):
        if re.search("[<>]",text): 
            print(self.name+": found unexpected < or > in text: "+text,file=sys.stderr)

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
                textFieldValue = self.getFieldValue(corpus,self.FIELDNAMETEXT,msgId)
                processedText = self.processText(textFieldValue)
                self.setFieldValue(corpus,self.FIELDNAMETEXT,msgId,processedText)
                OWWidget.progressBarSet(self,100*(msgId+1)/len(self.corpus))
        self.Outputs.corpus.send(self.corpus)
