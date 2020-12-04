from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.widget import OWWidget, Input, Output
from orangecontrib.text.corpus import Corpus
import orangehackathon.libs.LIWCLIB as LIWCLIB

# Create the widget
class LIWC(OWWidget):
    name = "LIWC"
    description = "Applies LIWC to each document in corpus"
    icon = "icons/compass.svg"

    class Inputs:
        corpus = Input("Corpus", Corpus)

    class Outputs:
        table = Output("Table", Table)

    def resetWidget(self):
        self.corpus = None

    def __init__(self):
        super().__init__()
        self.label = gui.widgetLabel(self.controlArea)
        self.resetWidget()

    @Inputs.corpus
    def inputAnalysis(self, corpus):
        self.resetWidget()
        self.corpus = corpus
        if self.corpus is None:
            self.label.setText("No corpus available")
            self.Outputs.table.send([])
        else:
            self.progressBarInit()
            self.liwcResultTable, liwcDictionary = LIWCLIB.processCorpus(self.corpus,windowId=self)
            self.progressBarFinished()
            self.label.setText("using dictionary "+liwcDictionary)
            self.Outputs.table.send(self.liwcResultTable)
