import xml.etree.ElementTree as ET
import re
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
import orangehackathon.libs.tactusloaderLIB as tactusloaderLIB

class TactusLoader(OWWidget):
    name = "Tactus Mail Loader"
    description = "Reads Tactus mails from directory"
    icon = "icons/mail.svg"
    category = "Hackathon"
    directory = ""
    patientId = tactusloaderLIB.DEFAULTPATIENTID

    def __init__(self):
        super().__init__()
        self.progress = gui.ProgressBar(self, 10)
        self.label = gui.widgetLabel(self.controlArea)
        self.drawWindow()

    class Outputs:
        data = Output("Corpus", Corpus)

    def drawWindow(self):
        form = QFormLayout()
        form.setFieldGrowthPolicy(form.AllNonFixedFieldsGrow)
        form.setVerticalSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft)
        gui.widgetBox(self.controlArea, True, orientation=form)
        form.addRow(
            "directory:",
            gui.lineEdit(
                None, self, "directory",
                controlWidth=100,
                orientation=Qt.Horizontal,
                tooltip="Tooltip",
                placeholderText=tactusloaderLIB.DEFAULTDIRECTORY))
        form.addRow(
            "patient id:",
            gui.lineEdit(
                None, self, "patientId",
                controlWidth=100,
                orientation=Qt.Horizontal,
                tooltip="Tooltip",
                placeholderText=tactusloaderLIB.DEFAULTPATIENTID))
        form.addRow(gui.button(None, self, 'prev', self.prev),gui.button(None, self, 'next', self.next))
        form.addRow(gui.button(None, self, 'load', self.load))

    def prev(self):
        self.patientId = str(int(self.patientId)-1)
        self.load()

    def next(self):
        self.patientId = str(int(self.patientId)+1)
        self.load()

    def load(self):
        patientFileName = tactusloaderLIB.makeFileName(self.patientId)
        table = tactusloaderLIB.processFile(self.directory,patientFileName)
        if len(table) > 0: 
            self.Outputs.data.send(Corpus.from_table(table.domain, table))
        else:
            self.label.setText("Warning: non-existent data file\n"+self.directory+"/"+patientFileName+"\nor empty corpus")

if __name__ == "__main__":
    WidgetPreview(TactusLoader).run()
