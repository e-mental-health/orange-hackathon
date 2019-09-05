from pathlib import Path

import pandas as pd
from Orange.widgets.widget import OWWidget, Output
from Orange.widgets import gui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout
from Orange.data.pandas_compat import table_from_frame
from orangecontrib.text import Corpus
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.data import Table, Domain
from Orange.data import TimeVariable, ContinuousVariable, DiscreteVariable, StringVariable

from orangehackathon.utils.mail2tsv import parse_enron_mail_old as parse_enron_mail

class EnronLoader(OWWidget):
    name = "Enron mail loader"
    description = "Reads Enron mails from directory"
    icon = "icons/turtle.svg"
    category = "Hackathon"
    directory = ''
    _glob='**/*.' # all files with names ending in . (*.) in all subdirectories (**)

    class Outputs:
        data = Output("Corpus", Corpus)

    def corpusDomain(self,mails):
        return(Domain([TimeVariable.make("date"),                                 \
                       DiscreteVariable.make("from",set([x[1] for x in mails])),  \
                       DiscreteVariable.make("to",  set([x[2] for x in mails]))], \
                metas=[StringVariable.make("file"),                               \
                       StringVariable.make("subject"),                            \
                       StringVariable.make("text"),                               \
                       StringVariable.make("extra")]))

    def drawWindow(self):
        form = QFormLayout()
        form.setFieldGrowthPolicy(form.AllNonFixedFieldsGrow)
        form.setVerticalSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft)
        gui.widgetBox(self.controlArea, True, orientation=form)
        form.addRow(
            "ENRON mail directory:",
            gui.lineEdit(
                None, self, "directory",
                controlWidth=200,
                orientation=Qt.Horizontal,
                tooltip="Tooltip",
                placeholderText="Directory"))
        form.addRow(
            "glob pattern:",
            gui.lineEdit(
                None, self, "_glob",
                controlWidth=100,
                orientation=Qt.Horizontal,
                tooltip="Tooltip",
                placeholderText=""))
        form.addRow(gui.button(None, self, 'load', self.load))

    def load(self):
        OWWidget.progressBarInit(self)
        files = list(Path(self.directory).glob(self._glob))
        mails = []
        self.progress.iter = len(files)
        for i, filename in enumerate(files):
            try:
                mails.append(parse_enron_mail(filename))
            except Exception as e:
                print(filename)
                print(e)
            self.progress.advance()

        domain = self.corpusDomain(mails)
        table = Table.from_list(domain,mails)
        self.Outputs.data.send(Corpus.from_table(table.domain, table))

    def __init__(self):
        super().__init__()
        self.progress = gui.ProgressBar(self, 10)
        self.drawWindow()

if __name__ == "__main__":
    WidgetPreview(EnronLoader).run()
