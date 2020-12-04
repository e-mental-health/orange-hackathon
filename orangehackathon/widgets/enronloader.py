from pathlib import Path

import os
import pandas as pd
from Orange.widgets.widget import OWWidget, Output
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout
from Orange.data.pandas_compat import table_from_frame
from orangecontrib.text import Corpus
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.data import Table, Domain
from Orange.data import TimeVariable, ContinuousVariable, DiscreteVariable, StringVariable

from orangehackathon.utils.mail2tsv import parse_enron_mail_old as parse_enron_mail

class EnronLoader(OWWidget):
    DEFAULTDIRECTORY = os.path.abspath(os.path.dirname(__file__)) + "../../../enron/"
    YESSTRING = "yes"

    name = "Enron mail loader"
    description = "Reads Enron mails from directory"
    icon = "icons/e.svg"
    directory = Setting(DEFAULTDIRECTORY)
    _glob = Setting('symes-k/*/*.') # all files with names ending in . (*.) in all subdirectories (*)

    class Outputs:
        data = Output("Corpus", Corpus)

    def corpusDomain(self,mails):
        return(Domain([TimeVariable.make("date"),                                       \
                       DiscreteVariable.make("from",      set([x[1] for x in mails])),  \
                       DiscreteVariable.make("to",        set([x[2] for x in mails])),  \
                       DiscreteVariable.make("duplicate", set([x[3] for x in mails]))], \
                metas=[StringVariable.make("file"),                                     \
                       StringVariable.make("subject"),                                  \
                       StringVariable.make("extra"),                                    \
                       StringVariable.make("text")]))

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
                controlWidth=100,
                orientation=Qt.Horizontal,
                tooltip="Tooltip",
                placeholderText=""))
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
        self.progressBarInit()
        files = list(Path(self.directory).glob(self._glob))
        mails = []
        seen = {}
        for i, filename in enumerate(files):
            try:
                mails.append(list(parse_enron_mail(filename)))
                key = "#".join([mails[-1][0],mails[-1][7]])
                if key in seen: 
                    mails[-1][3] = self.YESSTRING
                seen[key] = True
            except Exception as e:
                print(filename)
                print(e)
            self.progressBarSet(100*(i+1)/len(files))

        domain = self.corpusDomain(mails)
        table = Table.from_list(domain,mails)
        self.Outputs.data.send(Corpus.from_table(table.domain, table))
        self.progressBarFinished()

    def __init__(self):
        super().__init__()
        self.drawWindow()

if __name__ == "__main__":
    WidgetPreview(EnronLoader).run()
