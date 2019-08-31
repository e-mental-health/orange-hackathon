from pathlib import Path

import pandas as pd
from Orange.widgets.widget import OWWidget, Output
from Orange.widgets import gui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout
from Orange.data.pandas_compat import table_from_frame
from orangecontrib.text import Corpus
from Orange.widgets.utils.widgetpreview import WidgetPreview

from orangehackathon.utils.mail2tsv import parse_enron_mail_old as parse_enron_mail


class EnronLoader(OWWidget):
    name = "Load enron mail source directory"
    description = "Read mails directory"
    icon = "icons/turtle.svg"
    category = "Hackathon"
    directory = ''
    _glob='**/inbox/*.'

    class Outputs:
        data = Output("Corpus", Corpus)

    def load(self):
        files = list(Path(self.directory).glob(self._glob))
        self.progress.advance(0)
        mails = []
        self.progress.iter = len(files)
        for i, filename in enumerate(files):
            try:
                mails.append(parse_enron_mail(filename))
            except Exception as e:
                print(filename)
                print(e)
            self.progress.advance()

        table = table_from_frame(pd.DataFrame(mails))
        self.Outputs.data.send(Corpus.from_table(table.domain, table))

    def __init__(self):
        super().__init__()
        self.progress = gui.ProgressBar(self, 100)
        form = QFormLayout()
        form.setFieldGrowthPolicy(form.AllNonFixedFieldsGrow)
        form.setVerticalSpacing(25)
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


if __name__ == "__main__":
    WidgetPreview(EnronLoader).run()
