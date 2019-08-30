import re
import sys
import pandas as pd
from Orange.data import pandas_compat, Table
from Orange.widgets import gui
from Orange.widgets.widget import OWWidget, Input, Output
from nltk import word_tokenize
from orangecontrib.text.corpus import Corpus


# Create the widget
class LIWC(OWWidget):
    name = "LIWC"
    description = "Applies LIWC to each document in corpus"
    icon = "icons/LIWC.svg"
    N = 20
    EMPTYLIST = []
    EMPTYSTRING = ""
    FIELDNAMETEXT = "text"
    FIELDNAMEEXTRA = "extra"
    LIWCDIR = 'C:\\Users\\Auke\\Documents\\Atlas\\Semester 6\\Thesis\\WWWFW\\Hackathon\\'
    LIWCFILE = "\\LIWC-DO-NOT-DISTRIBUTE.txt"
    COMMAND = sys.argv.pop(0)
    TEXTBOUNDARY = "%"
    NBROFTOKENS = "NBROFTOKENS"
    NBROFMATCHES = "Number of Matches"
    MAXPREFIXLEN = 10
    TOKENID = 0
    LEMMAID = 1
    NUMBER = "number"
    numberId = -1

    class Inputs:
        corpus = Input("Corpus", Corpus)

    class Outputs:
        LIWC_table = Output("Table", Table)
        corpus = Output("Corpus", Corpus)

    def resetWidget(self):
        self.corpus = None

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
        text = re.sub("</*line>", " ", text)
        text = re.sub(">>+", " ", text)
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
        features = {}
        for line in inFile:
            line = line.strip()
            if line == self.TEXTBOUNDARY:
                break
            fields = line.split()
            featureId = fields.pop(0)
            featureName = " ".join(fields)
            features[featureId] = featureName
            if featureName == self.NUMBER: self.numberId = featureId
        return (features)

    def makeUniqueElements(self, inList):
        outList = []
        seen = {}
        for element in inList:
            if not element in seen:
                outList.append(element)
                seen[element] = True
        return outList

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
        return (words, prefixes)

    def readLiwc(self, inFileName):
        try:
            inFile = open(inFileName, "r")
        except Exception as e:
            sys.exit(self.COMMAND + ": cannot read LIWC dictionary " + inFileName)
        self.readEmpty(inFile)
        features = self.readFeatures(inFile)
        words, prefixes = self.readWords(inFile)
        inFile.close()
        return (features, words, prefixes)

    def findLongestPrefix(self, prefixes, word):
        while not word in prefixes and len(word) > 0:
            chars = list(word)
            chars.pop(-1)
            word = "".join(chars)
        return (word)

    def addFeatureToCounts(self, counts, feature):
        if feature in counts:
            counts[feature] += 1
        else:
            counts[feature] = 1

    def text2liwc(self, words, prefixes, tokens):
        counts = {}
        for word in tokens:
            if word in words:
                self.addFeatureToCounts(counts, self.NBROFMATCHES)

                for feature in words[word]:
                    if feature.isdigit():
                        self.addFeatureToCounts(counts, feature)

            longestPrefix = self.findLongestPrefix(prefixes, word)
            if longestPrefix != "":
                self.addFeatureToCounts(counts, self.NBROFMATCHES)
                for feature in prefixes[longestPrefix]:
                    self.addFeatureToCounts(counts, feature)
            if self.isNumber(word):
                self.addFeatureToCounts(counts, self.NBROFMATCHES)
                self.addFeatureToCounts(counts, "Number count")
        return counts

    def liwcResults(self, text, words, prefixes):
        tokens = self.prepareText(text)
        counts = self.text2liwc(words, prefixes, tokens)
        return counts

    # Iterate over documents in corpus

    # Iterate over text per document, apply liwc to each word

    @Inputs.corpus
    def inputAnalysis(self, corpus):
        self.resetWidget()
        self.corpus = corpus
        if self.corpus is None:
            self.label.setText("No corpus available")
        else:
            self.fieldIdText = self.getFieldId(self.corpus, self.FIELDNAMETEXT)
            self.fieldIdExtra = self.getFieldId(self.corpus, self.FIELDNAMEEXTRA)
            features, words, prefixes = self.readLiwc(self.LIWCDIR + self.LIWCFILE)
            for msgId in range(0, len(self.corpus.metas)):
                text = str(self.corpus.metas[msgId][self.fieldIdText])
                result = self.liwcResults(text, words, prefixes)
                self.corpus.metas[msgId][self.fieldIdExtra] = result

        self.Outputs.corpus.send(self.corpus)






