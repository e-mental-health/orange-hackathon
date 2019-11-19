import os
import re
import sys
import pandas as pd
import numpy as np
from Orange.data import pandas_compat, Domain, Table
from Orange.widgets import gui
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.data import TimeVariable, ContinuousVariable, DiscreteVariable, StringVariable
from nltk import word_tokenize
from orangecontrib.text.corpus import Corpus
from operator import itemgetter

# Create the widget
class LIWC(OWWidget):
    name = "LIWC"
    description = "Applies LIWC to each document in corpus"
    icon = "icons/compass.svg"
    N = 20
    EMPTYLIST = []
    EMPTYSTRING = ""
    FIELDNAMEFILE = "file"
    FIELDNAMETEXT = "text"
    FIELDNAMEEXTRA = "extra"
    FIELDNAMEMSGID = "msg id"
    LIWCFILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Dicts' , 'LIWC-DO-NOT-DISTRIBUTE.txt')
    COMMAND = sys.argv.pop(0)
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

    class Inputs:
        corpus = Input("Corpus", Corpus)

    class Outputs:
        table = Output("Table", Corpus)

    def resetWidget(self):
        self.corpus = None
        self.progress= gui.ProgressBar(self, 10)

    def __init__(self):
        super().__init__()
        self.label = gui.widgetLabel(self.controlArea)
        self.resetWidget()

    def getFieldId(self,corpus,fieldName):
        fieldId = -1
        for i in range(0,len(corpus.domain.metas)):
            if str(corpus.domain.metas[i]) == fieldName:
                fieldId = i
        return(fieldId)


    def prepareText(self, text):
        text = re.sub("</*line>", self.SPACE, text)
        text = re.sub(">>+", self.SPACE, text)
        return word_tokenize(text)

    def isNumber(self, string):
        return string.lstrip("-").replace(".", "1").isnumeric()

    def readEmpty(self, inFile):
        text = ""
        for line in inFile:
            line = line.strip()
            if line == self.TEXTBOUNDARY:
                break
            text += line + "\n"
        if text != "":
            sys.exit(self.COMMAND + ": liwc dictionary starts with unexpected text: " + text)

    def readFeatures(self, inFile):
        featureNames = {}
        for line in inFile:
            line = line.strip()
            if line == self.TEXTBOUNDARY:
                break
            fields = line.split()
            featureId = fields.pop(0)
            featureName = self.SPACE.join(fields)
            featureNames[featureId] = featureName
            if featureName == self.NUMBER: self.numberId = featureId
        return(featureNames)

    def makeUniqueElements(self, inList):
        outList = []
        seen = {}
        for element in inList:
            if not element in seen:
                outList.append(element)
                seen[element] = True
        return(outList)

    def readWords(self, inFile):
        words = {}
        prefixes = {}
        for line in inFile:
            line = line.strip()
            if line == self.TEXTBOUNDARY: break
            fields = line.split()
            word = fields.pop(0).lower()
            word = re.sub(r"\*$", "", word)
            if re.search(r"-$", word):
                word = re.sub(r"-$", "", word)
                if not word in prefixes:
                    prefixes[word] = fields
                else:
                    words[word] = self.makeUniqueElements(words[word] + fields)
            else:
                if not word in words:
                    words[word] = fields
                else:
                    words[word] = self.makeUniqueElements(words[word] + fields)
        return(words, prefixes)

    def readLiwc(self, inFileName):
        try:
            inFile = open(inFileName, "r")
        except Exception as e:
            sys.exit(self.COMMAND + ": cannot read LIWC dictionary " + inFileName)
        self.readEmpty(inFile)
        featureNames = self.readFeatures(inFile)
        words, prefixes = self.readWords(inFile)
        inFile.close()
        return(featureNames, words, prefixes)

    def findLongestPrefix(self, prefixes, word):
        while not word in prefixes and len(word) > 0:
            chars = list(word)
            chars.pop(-1)
            word = "".join(chars)
        return(word)

    def addFeatureToCounts(self, counts, feature, featureNames=None):
        key = feature
        if featureNames != None and feature in featureNames: 
            key = feature+self.SPACE+featureNames[feature]
        if key in counts:
            counts[key] += 1
        else:
            counts[key] = 1

    def text2liwc(self, words, prefixes, featureNames, tokens):
        counts = {}
        for word in tokens:
            if word in words:
                self.addFeatureToCounts(counts, self.NBROFMATCHES)
                for feature in words[word]:
                    if feature.isdigit():
                        self.addFeatureToCounts(counts, feature, featureNames)
            longestPrefix = self.findLongestPrefix(prefixes, word)
            if longestPrefix != "":
                self.addFeatureToCounts(counts, self.NBROFMATCHES)
                for feature in prefixes[longestPrefix]:
                    self.addFeatureToCounts(counts, feature, featureNames)
            if self.isNumber(word):
                self.addFeatureToCounts(counts, self.NBROFMATCHES)
                self.addFeatureToCounts(counts, "Number count")
        return(counts)

    def liwcResults(self, text, words, prefixes, featureNames):
        tokens = self.prepareText(text)
        counts = self.text2liwc(words, prefixes, featureNames, tokens)
        return(counts)

    def getColumnNames(self,thisList):
        columnNames = []
        for row in thisList:
            for columnName in row:
                if not columnName in columnNames: columnNames.append(columnName)
        return(columnNames)

    def list2table(self,thisList):
        columnNames = self.getColumnNames(thisList)
        table = []
        for row in thisList:
            table.append(row)
            for columnName in columnNames:
                if not columnName in row: table[-1][columnName] = '0'
        return(table,columnNames)

    def keyCombine(self,number,string):
        if string == "": 
            if number > 0: return(str(number))
            else: return("")
        elif number > 0: return(str(number)+self.SEPARATOR+string)
        else: return(string)

    def keySplit(self,key):
         keyParts = key.split(self.SEPARATOR)
         if len(keyParts) > 0 and re.match("^\d+$",keyParts[0]):
             number = keyParts.pop(0)
             return(int(number),self.SEPARATOR.join(keyParts))
         else:
             return(0,self.SEPARATOR.join(keyParts))

    def sortKeys(self,keys):
        splitKeys = [self.keySplit(k) for k in keys]
        sortedKeys = sorted(splitKeys,key=itemgetter(0,1))
        return([self.keyCombine(k[0],k[1]) for k in sortedKeys])

    def dataCombine(self,corpus,liwcResultList):
        liwcResultTable,columnNames = self.list2table(liwcResultList)
        self.fieldIdFile = self.getFieldId(self.corpus, self.FIELDNAMEFILE)
        domain = [ContinuousVariable(name=self.FIELDNAMEMSGID)]+list(corpus.domain)
        for columnName in self.sortKeys(columnNames):
            domain.append(ContinuousVariable(name=columnName))
        dataOut = []
        metasOut = []
        for i in range(0,len(corpus)):
            fileName = corpus.metas[i][self.fieldIdFile]
            metasOut.append(fileName)
            row = [i+1]+list(corpus[i].values())
            for columnName in self.sortKeys(columnNames):
                if not re.match("^\d+$",columnName) or int(liwcResultTable[i][self.NBROFMATCHES]) == 0:
                    row.append(int(liwcResultTable[i][columnName]))
                else:
                    row.append(100.0*float(liwcResultTable[i][columnName])/float(liwcResultTable[i][self.NBROFMATCHES]))
            dataOut.append(row)
        table = Table.from_numpy(Domain(domain),np.array(dataOut))
        return(table) 

    @Inputs.corpus
    def inputAnalysis(self, corpus):
        self.resetWidget()
        OWWidget.progressBarInit(self)
        self.corpus = corpus
        if self.corpus is None:
            self.label.setText("No corpus available")
        else:
            self.fieldIdText = self.getFieldId(self.corpus, self.FIELDNAMETEXT)
            self.fieldIdExtra = self.getFieldId(self.corpus, self.FIELDNAMEEXTRA)
            featureNames, words, prefixes = self.readLiwc(self.LIWCFILE)
            self.progress.iter = len(self.corpus)
            liwcResultList = []
            for msgId in range(0, len(self.corpus.metas)):
                text = str(self.corpus.metas[msgId][self.fieldIdText])
                liwcResultList.append(self.liwcResults(text, words, prefixes, featureNames))
                self.progress.advance()
            self.table = self.dataCombine(self.corpus,liwcResultList)
        self.Outputs.table.send(self.table)
