import xml.etree.ElementTree as ET
import os
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
    ALLFILES = "*"
    HELPTEXT = "use patient id * for reading all AdB* files"
    name = "Tactus Mail Loader"
    description = "Reads Tactus mails from directory"
    icon = "icons/mail.svg"
    category = "Hackathon"
    directory = ""
    patientId = tactusloaderLIB.DEFAULTPATIENTID
    directory = tactusloaderLIB.DEFAULTDIRECTORY

    def __init__(self):
        super().__init__()
        self.progress = gui.ProgressBar(self, 10)
        self.label = gui.widgetLabel(self.controlArea)
        self.label.setText(self.HELPTEXT)
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
                placeholderText=str(tactusloaderLIB.DEFAULTPATIENTID)))
        form.addRow(gui.button(None, self, 'load', self.load))
        form.addRow(gui.button(None, self, 'prev', self.prev),gui.button(None, self, 'next', self.next))

    def prev(self):
        if self.patientId != self.ALLFILES:
            self.patientId = str(int(self.patientId)-1)
            self.load()

    def next(self):
        if self.patientId != self.ALLFILES:
            self.patientId = str(int(self.patientId)+1)
            self.load()

    def readAllFiles(self,directory):
        fileNames = os.listdir(directory)
        allMails = []
        for fileName in fileNames:
            if re.search(r"^"+tactusloaderLIB.INFILEPREFIX,fileName):
                table,mails = tactusloaderLIB.processFile(self.directory,fileName)
                allMails.extend(mails)
        largeTable = tactusloaderLIB.mails2table(allMails)
        return(largeTable)

    def load(self):
        if self.patientId == self.ALLFILES: table = self.readAllFiles(self.directory)
        else: 
            patientFileName = tactusloaderLIB.makeFileName(self.patientId)
            table,mails = tactusloaderLIB.processFile(self.directory,patientFileName)
        if len(table) > 0: 
            self.label.setText(self.HELPTEXT)
            self.Outputs.data.send(Corpus.from_table(table.domain, table))
        else:
            self.label.setText("Warning: non-existent data file\n"+self.directory+"/"+patientFileName+"\nor empty corpus")

if __name__ == "__main__":
    WidgetPreview(TactusLoader).run()
