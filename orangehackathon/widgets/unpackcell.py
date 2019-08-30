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
from orangecontrib.text.corpus import Corpus, Table
from Orange.data import domain, table, pandas_compat
from Orange.widgets.data import owfeatureconstructor
from itertools import chain
from nltk import word_tokenize
import re
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class Unpackcell(OWWidget):
    name="Unpack cell"
    description= 'transform the daap data in order to be visualised'
    icon= "icons/MarkDuplicates.svg"
    FIELDNAMEDATE = "date"
    FIELDNAMETEXT = "text"
    FIELDNAMEEXTRA = "extra"
    EMPTYSTRING = ""
    
    class Inputs:
        corpus= Input("Corpus", Corpus)
        
    class Outputs:
        table= Output("Table", Table)

    def resetWidget(self):
        self.corpus = None
        self.table=None
        
    def __init__(self):
        super().__init__()
        self.label= gui.widgetLabel(self.controlArea)
        self.progress= gui.ProgressBar(self, 100)
        self.resetWidget()

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
        if self.corpus is None:
            self.label.setText("No corpus available")
        else:
            text = self.EMPTYSTRING
            self.fieldIdExtra = self.getFieldId(self.corpus,self.FIELDNAMEEXTRA)
            self.fieldIdText = self.getFieldId(self.corpus,self.FIELDNAMETEXT)
            for msgId in range(0,len(self.corpus.metas)):
                if self.corpus.metas[msgId][self.fieldIdExtra] is not None:
                    text=str(self.corpus.metas[msgId][self.fieldIdExtra])
                else:
                    text=str(self.corpus.metas[msgId][self.fieldIdText])
                data=text[:-1]
                data=data[1:].split(',')
                data=list(map(float,data))
                datafra=pd.DataFrame(data)
                datafra['new_col'] = range(1, len(datafra) + 1)
                self.table=pandas_compat.table_from_frame(datafra)                    
        self.Outputs.table.send(self.table)    

    