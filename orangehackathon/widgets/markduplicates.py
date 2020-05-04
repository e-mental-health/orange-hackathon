from Orange.widgets import gui
from Orange.data import StringVariable
from orangecontrib.text.corpus import Corpus
from Orange.widgets.widget import OWWidget, Input, Output
import orangehackathon.libs.markduplicatesLIB as markduplicatesLIB

class MarkDuplicates(OWWidget):
    name = "Mark Duplicates"
    description = "Mark duplicate text parts in corpus"
    icon = "icons/globe.svg"
    want_main_area = False
    N = 20
    EMPTYSTRING = ""
    FIELDNAMEDATE = "date"
    FIELDNAMETEXT = "text"
    FIELDNAMECOORDINATES = "coordinates"

    class Inputs:
        corpus = Input("Corpus", Corpus)

    class Outputs:
        corpus = Output("Corpus", Corpus)

    def resetWidget(self):
        self.corpus = None

    def __init__(self):
        super().__init__()
        self.label = gui.widgetLabel(self.controlArea)
        self.progress = gui.ProgressBar(self, 1)
        self.resetWidget()
    
    @Inputs.corpus
    def inputAnalysis(self, corpus):
        self.resetWidget()
        self.corpus = corpus
        OWWidget.progressBarInit(self)
        if self.corpus is None:
            self.label.setText("No corpus available")
        else:
            self.label.setText("Processing corpus")
            self.corpus = markduplicatesLIB.processCorpus(corpus,progress=self.progress)
        self.Outputs.corpus.send(self.corpus)
