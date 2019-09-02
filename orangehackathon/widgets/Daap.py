# -*- coding: utf-8 -*-
#"""
#Created on Thu Aug 29 14:35:40 2019
#
#@author: Gyan de Haan building on the work of eriktks
#"""

from math import exp, pow
import sys
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui
from orangecontrib.text.corpus import Corpus
from Orange.data.domain import filter_visible
from Orange.widgets.data import owfeatureconstructor
from itertools import chain
from nltk import word_tokenize
import re
import datetime
import numpy as np

class Daap(OWWidget):
    name="Daap analysis"
    description= 'Do a Daap analysis on the selected corpus'
    icon= "icons/recycle.svg"
    FIELDNAMEDATE = "date"
    FIELDNAMETEXT = "text"
    FIELDNAMEEXTRA = "extra"
    DAAPDICTFILE= '/home/erikt/projects/e-mental-health/enron/orange-hackathon/orangehackathon/widgets/Dicts/WRAD.Wt'
    COMMAND = sys.argv[0]
    movingWeights = {}
    WINDOWSIZE = 100
    EMPTYSTRING = ""
    
    class Inputs:
        corpus= Input("Corpus", Corpus)
        
    class Outputs:
        corpus= Output("Corpus", Corpus)
        
    def resetWidget(self):
        self.corpus = None
        
    def __init__(self):
        super().__init__()
        self.label= gui.widgetLabel(self.controlArea)
        self.progress= gui.ProgressBar(self, 100)
        self.resetWidget()
        
        
    def prepareText(self,text):
        text = re.sub("</*line>"," ",text)
        text = re.sub(">>+"," ",text)
        text = " ".join(word_tokenize(text))
        return(text)
        
    def readDict(self, inFileName):
        try: 
            dictionary = {}
            inFile = open(inFileName,"r")
            for line in inFile:
                line = line.strip()
                token,weight = line.split()
                dictionary[token] = float(weight)
            inFile.close()
            return(dictionary)
        except Exception as e: 
            sys.exit(self.COMMAND+": error processing file "+inFileName+": "+str(e))
        
        
    def readText(self,):
        text=""
        for line in sys.stdin:text+=line
        return(text)
        
    def getWeightList(self,text,dictionary):
        weightList = []
        for token in text.split():
            if token in dictionary: weightList.append(dictionary[token])
            else: weightList.append(0.0)
        return(weightList) 
    
    def getRealContextIndex(self,contextIndex,weightListLen):
        switchCounter = 0
        while contextIndex < 0:
            contextIndex += weightListLen
            switchCounter += 1
        if switchCounter % 2 != 0:
            contextIndex = weightListLen-1-contextIndex
        while contextIndex >= weightListLen:
            contextIndex -= weightListLen
            switchCounter += 1
        if switchCounter % 2 != 0:
            contextIndex = weightListLen-1-contextIndex
        return(contextIndex)

    def eFunction(self,windowSize,index):
        return(exp(-2.0*pow(windowSize,2.0) * \
                   (pow(windowSize,2.0)+pow(index,2.0)) / \
                   pow(pow(windowSize,2.0)-pow(index,2.0),2.0)))
    
    def movingWeight(self,index,windowSize):
        if str(index) in self.movingWeights: return(self.movingWeights[str(index)])
        elif index <= -windowSize or index >= windowSize: 
            self.movingWeights[str(index)] = 0.0
            return(self.movingWeights[str(index)])
        else:
            nominator = self.eFunction(windowSize,index)
            denominator = 0.0
            for j in range(1-windowSize,windowSize):
                denominator += self.eFunction(windowSize,j)
            self.movingWeights[str(index)] = nominator/denominator
            return(self.movingWeights[str(index)])
    
    def computeAverage(self,weightList,index,windowSize):
        total = 0
        for contextIndex in range(index-windowSize+1,index+windowSize):
            realContextIndex = self.getRealContextIndex(contextIndex,len(weightList))
            total += weightList[realContextIndex]*self.movingWeight(contextIndex-index,windowSize)
        return(total)
    
    def computeaverageWeights(self,weightList,windowSize):
        averageWeights = []
        for i in range(0,len(weightList)):
            averageWeights.append(self.computeAverage(weightList,i,windowSize))
        return(averageWeights)
    
    def daap(self,text,windowSize=WINDOWSIZE):
        self.movingWeights.clear()
        dictionary = self.readDict(self.DAAPDICTFILE)
        weightList = self.getWeightList(text.lower(),dictionary)
        averageWeights = self.computeaverageWeights(weightList,windowSize)
        return(averageWeights)

    def getFieldId(self,corpus,fieldName):
        fieldId = -1
        for i in range(0,len(corpus.domain.metas)):
            if str(corpus.domain.metas[i]) == fieldName:
                fieldId = i
        return(fieldId)
    
    @Inputs.corpus
    def inputAnalysis(self, corpus):
        self.resetWidget()
        self.corpus= corpus
        OWWidget.progressBarInit(self)
        if self.corpus is None:
            self.label.setText("No corpus available")
        else:
            text = self.EMPTYSTRING
            self.fieldIdExtra = self.getFieldId(self.corpus,self.FIELDNAMEEXTRA)
            self.fieldIdText = self.getFieldId(self.corpus,self.FIELDNAMETEXT)
            for msgId in range(0,len(self.corpus.metas)):
                text=self.prepareText(str(self.corpus.metas[msgId][self.fieldIdText]))
                averageWeights = self.daap(text)
                OWWidget.progressBarSet(self,len(self.corpus))
                owfeatureconstructor.OWFeatureConstructor()
                self.corpus.metas[msgId][self.fieldIdExtra]=averageWeights
        self.Outputs.corpus.send(self.corpus)    
