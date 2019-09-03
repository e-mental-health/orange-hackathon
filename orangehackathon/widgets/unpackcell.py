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
from Orange.data import Table, Domain
from Orange.data import TimeVariable, ContinuousVariable, DiscreteVariable, StringVariable

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
        table = Output("Table", Table)

    def resetWidget(self):
        self.corpus = None
        self.table=None
        
    def __init__(self):
        super().__init__()
        self.label= gui.widgetLabel(self.controlArea)
        self.resetWidget()

    def getFieldValue(self,corpus,fieldName,rowId):
        for i in range(0,len(corpus.domain)):
            if corpus.domain[i].name == fieldName:
                return(corpus[rowId].list[i])
        for i in range(0,len(corpus.domain.metas)):
            if corpus.domain.metas[i].name == fieldName:
                return(corpus[rowId].metas[i])
        sys.exit("getFieldValue: field name not found: "+fieldName)

    @Inputs.corpus
    def inputAnalysis(self, corpus):
        self.resetWidget()
        self.corpus= corpus
        if self.corpus is None:
            print("Unpack cell: No corpus available")
            self.label.setText("No corpus available")
        else:
            self.label.setText("Processing corpus")
            data = []
            valueId = 0
            for msgId in range(0,len(self.corpus)):
                date = self.getFieldValue(corpus,self.FIELDNAMEDATE,msgId)
                for value in self.getFieldValue(corpus,self.FIELDNAMEEXTRA,msgId):
                     data.append([valueId,date,value])
                     valueId += 1
            domain = Domain([ContinuousVariable.make("id"),TimeVariable.make("date"),ContinuousVariable.make("extra")],metas=[])
            table = Table.from_list(domain,data)
            self.Outputs.table.send(table)    
