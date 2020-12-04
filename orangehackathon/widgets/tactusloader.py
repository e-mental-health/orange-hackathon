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
    ALLFILESPYTHON = ".*"
    HELPTEXT = "use patient id * for reading all AdB* files"
    DEFAULTFILEPATTERN = 1
    name = "Tactus Mail Loader"
    description = "Reads Tactus mails from directory"
    icon = "icons/mail.svg"
    directory = ""
    filePattern = DEFAULTFILEPATTERN
    directory = tactusloaderLIB.DEFAULTDIRECTORY

    def __init__(self):
        super().__init__()
        self.label = gui.widgetLabel(self.controlArea)
        # self.label.setText(self.HELPTEXT)
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
                None, self, "filePattern",
                controlWidth=100,
                orientation=Qt.Horizontal,
                tooltip="Tooltip",
                placeholderText=str(self.DEFAULTFILEPATTERN)))
        form.addRow(gui.button(None, self, 'load', self.load))
        form.addRow(gui.button(None, self, 'prev', self.prev),gui.button(None, self, 'next', self.next))

    def prev(self):
        if re.search("^\d+$",str(self.filePattern)):
            self.filePattern = str(int(self.filePattern)-1)
            self.load()

    def next(self):
        if re.search("^\d+$",str(self.filePattern)):
            self.filePattern = str(int(self.filePattern)+1)
            self.load()

    def readFiles(self,directory,filePattern):
        allMails = []
        fileCounter = 0
        fileNames = sorted(os.listdir(directory))
        if filePattern == self.ALLFILES: filePattern = self.ALLFILESPYTHON
        for fileName in fileNames:
            if re.search(r"^"+tactusloaderLIB.INFILEPREFIX,fileName) and \
               re.search(filePattern,fileName):
                table,mails = tactusloaderLIB.processFile(self.directory,fileName)
                allMails.extend(mails)
                fileCounter += 1
                self.progressBarSet(100*fileCounter/len(fileNames))
        largeTable = tactusloaderLIB.mails2table(allMails)
        return(largeTable,fileCounter)

    def load(self):
        self.label.setText("")
        self.progressBarInit()
        if re.search("^\d+$",str(self.filePattern)):
            patientFileName = tactusloaderLIB.makeFileName(self.filePattern)
            table,mails = tactusloaderLIB.processFile(self.directory,patientFileName)
            self.progressBarSet(100)
            self.label.setText("read 1 file")
        else: 
            table,fileCounter = self.readFiles(self.directory,self.filePattern)
            self.label.setText("read "+str(fileCounter)+" files")
        self.progressBarFinished()
        if len(table) > 0: 
            self.Outputs.data.send(Corpus.from_table(table.domain, table))
        else:
            self.label.setText("Warning: non-existent data file\n"+self.directory+"/"+patientFileName+"\nor empty corpus")

if __name__ == "__main__":
    WidgetPreview(TactusLoader).run()
