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

import xml.etree.ElementTree as ET
import re

class TactusLoader(OWWidget):
    name = "Tactus Mail Loader"
    description = "Reads Tactus mails from directory"
    icon = "icons/mail.svg"
    category = "Hackathon"
    directory = ""
    patientId = ""
    DEFAULTDIRECTORY = "/home/erikt/projects/e-mental-health/usb/tmp/20190624"
    DEFAULTPATIENTID = "1"
    MESSAGES = "./Messages/Message"
    SENDER = "Sender"
    RECIPIENT = "Recipients"
    SENDER = "Sender"
    SUBJECT = "Subject"
    BODY = "Body"
    DATESENT = "DateSent"
    CLIENT = "CLIENT"
    COUNSELOR = "COUNSELOR"
    MAILDATEID = 3
    MAILBODYID = 5
    MAXIDLEN = 4
    INFILEPREFIX = "AdB"
    INFILESUFFIX = "-an.xml"

    class Outputs:
        data = Output("Corpus", Corpus)

    def corpusDomain(self,mails):
        return(Domain([TimeVariable.make("date"),                                 \
                       DiscreteVariable.make("from",set([x[1] for x in mails])),  \
                       DiscreteVariable.make("to",  set([x[2] for x in mails]))], \
                metas=[StringVariable.make("file"),                               \
                       StringVariable.make("subject"),                            \
                       StringVariable.make("text")]))

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
                placeholderText=self.DEFAULTDIRECTORY))
        form.addRow(
            "patient id:",
            gui.lineEdit(
                None, self, "patientId",
                controlWidth=100,
                orientation=Qt.Horizontal,
                tooltip="Tooltip",
                placeholderText=self.DEFAULTPATIENTID))
        form.addRow(gui.button(None, self, 'load', self.load))

    def makeFileName(self,patientId):
        if patientId == "": patientId = self.DEFAULTPATIENTID
        while (len(patientId) < self.MAXIDLEN): patientId = "0"+patientId
        return(self.INFILEPREFIX+patientId+self.INFILESUFFIX)

    def sentenceSplit(self,text):
        tokens = text.split()
        sentence = []
        sentences = []
        for token in tokens:
            sentence.append(token)
            if not re.search(r"[a-zA-Z0-9'\"]",token):
                sentences.append(" ".join(sentence))
                sentence = []
        if len(sentence) > 0: sentences.append(" ".join(sentence))
        return(sentences)

    def cleanupMails(self,clientMails, counselorMails):
        clientSentenceDates = {}
        counselorSentenceDates = {}
        for i in range(0,len(clientMails)):
            date = clientMails[i][self.MAILDATEID]
            body = clientMails[i][self.MAILBODYID]
            sentences = self.sentenceSplit(body)
            for s in sentences:
                if (s in clientSentenceDates and date < clientSentenceDates[s]) or \
                    not s in clientSentenceDates:
                    clientSentenceDates[s] = date
        for i in range(0,len(counselorMails)):
            date = counselorMails[i][self.MAILDATEID]
            body = counselorMails[i][self.MAILBODYID]
            sentences = self.sentenceSplit(body)
            for s in sentences:
                if s in clientSentenceDates and date < clientSentenceDates[s]:
                    counselorSentenceDates[s] = date
                    del(clientSentenceDates[s])
                elif s in counselorSentenceDates and date < counselorSentenceDates[s]:
                    counselorSentenceDates[s] = date
                elif not s in clientSentenceDates and not s in counselorSentenceDates:
                    counselorSentenceDates[s] = date
        for i in range(0,len(clientMails)):
            date = clientMails[i][self.MAILDATEID]
            body = clientMails[i][self.MAILBODYID]
        return(clientMails)

    def cleanupText(self,text):
        if text == None: return("")
        text = re.sub(r"\s+"," ",text)
        text = re.sub(r"^ ","",text)
        text = re.sub(r" $","",text)
        return(text)
    
    def anonymizeCounselor(self,name):
        if name != self.CLIENT: return(self.COUNSELOR)
        else: return(name)
    
    def getEmailData(self,root,patientFileName):
        clientMails = []
        counselorMails = []
        OWWidget.progressBarInit(self)
        self.progress.iter = 1
        for message in root.findall(self.MESSAGES):
            body = ""
            date = ""
            recipient = ""
            sender = ""
            subject = ""
            for child in message:
                if child.tag == self.SENDER: 
                    sender = self.anonymizeCounselor(self.cleanupText(child.text))
                elif child.tag == self.RECIPIENT: 
                    recipient = self.anonymizeCounselor(self.cleanupText(child.text))
                elif child.tag == self.DATESENT: date = self.cleanupText(child.text)
                elif child.tag == self.SUBJECT: subject = self.cleanupText(child.text)
                elif child.tag == self.BODY: body = self.cleanupText(child.text)
            if sender == self.CLIENT: clientMails.append([date,sender,recipient,patientFileName,subject,body])
            else: counselorMails.append([date,sender,recipient,patientFileName,subject,body])
        clientMails = self.cleanupMails(clientMails,counselorMails)
        counselorMails = self.cleanupMails(counselorMails,clientMails)
        allMails = clientMails
        allMails.extend(counselorMails)
        self.progress.advance()
        return(sorted(allMails,key=lambda subList:subList[self.MAILDATEID]))

    def processFile(self,directory,patientFileName):
        if directory == "": directory = self.DEFAULTDIRECTORY
        tree = ET.parse(directory+"/"+patientFileName)
        root = tree.getroot()
        return(self.getEmailData(root,patientFileName))

    def load(self):
        patientFileName = self.makeFileName(self.patientId)
        mails = self.processFile(self.directory,patientFileName)

        domain = self.corpusDomain(mails)
        table = Table.from_list(domain,mails)
        self.Outputs.data.send(Corpus.from_table(table.domain, table))

    def __init__(self):
        super().__init__()
        self.progress = gui.ProgressBar(self, 10)
        self.drawWindow()

if __name__ == "__main__":
    WidgetPreview(TactusLoader).run()
