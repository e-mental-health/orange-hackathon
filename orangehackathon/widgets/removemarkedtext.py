from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui
from orangecontrib.text.corpus import Corpus
import orangehackathon.libs.removemarkedtextLIB as removemarkedtextLIB

class MarkDuplicates(OWWidget):
    name = "Remove Marked Text"
    description = "Remove marked text from corpus"
    icon = "icons/default.svg"
    N = 20
    EMPTYSTRING = ""
    FIELDNAMETEXT = "text"

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
        self.resetWidget()
    
    @Inputs.corpus
    def inputAnalysis(self, corpus):
        self.resetWidget()
        self.corpus = corpus
        if self.corpus is None:
            self.label.setText("No corpus available")
        else:
            self.label.setText("Processing corpus")
            self.corpus = removemarkedtextLIB.processCorpus(self.corpus)
        self.Outputs.corpus.send(self.corpus)
