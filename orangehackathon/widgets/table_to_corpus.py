from Orange.data import Table
from Orange.widgets.widget import OWWidget, Output, Input
from orangecontrib.text import Corpus


class TableToCorpus(OWWidget):
    name = "Table -> Corpus"
    description = "Convert Table to Corpus"
    icon = "icons/MarkDuplicates.svg"
    category = "Hackathon"

    class Inputs:
        table = Input("Table", Table)

    class Outputs:
        corpus = Output("Corpus", Corpus)

    @Inputs.table
    def convert(self, table):
        if table:
            self.Outputs.corpus.send(Corpus.from_table(table.domain, table))

