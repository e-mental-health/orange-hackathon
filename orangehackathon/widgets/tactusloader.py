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
    icon = "icons/turtle.svg"
    category = "Hackathon"
    directory = ""
    patientId = ""
    DEFAULTDIR = "/home/erikt/projects/e-mental-health/usb/tmp/20190624"
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

    class Outputs:
        data = Output("Corpus", Corpus)

    def corpusDomain(self,mails):
        return(Domain([TimeVariable.make("date"),                                 \
                       DiscreteVariable.make("from",set([x[1] for x in mails])),  \
                       DiscreteVariable.make("to",  set([x[2] for x in mails]))], \
                metas=[StringVariable.make("id"),                                 \
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
            "directory:",
            gui.lineEdit(
                None, self, "directory",
                controlWidth=100,
                orientation=Qt.Horizontal,
                tooltip="Tooltip",
                placeholderText=self.DEFAULTDIR))
        form.addRow(
            "patient id:",
            gui.lineEdit(
                None, self, "patientId",
                controlWidth=100,
                orientation=Qt.Horizontal,
                tooltip="Tooltip",
                placeholderText=self.DEFAULTPATIENTID))
        form.addRow(gui.button(None, self, 'load', self.load))

    def makeFileName(self,directory,patientId):
        if patientId == "": patientId = self.DEFAULTPATIENTID
        if directory == "": directory = self.DEFAULTDIR
        while (len(patientId) < self.MAXIDLEN): patientId = "0"+patientId
        return(directory+"/AdB"+patientId+"-an.xml")

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
    
    def getEmailData(self,root,thisId):
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
            if sender == self.CLIENT: clientMails.append([date,sender,recipient,thisId,subject,body])
            else: counselorMails.append([date,sender,recipient,thisId,subject,body])
        clientMails = self.cleanupMails(clientMails,counselorMails)
        counselorMails = self.cleanupMails(counselorMails,clientMails)
        allMails = clientMails
        allMails.extend(counselorMails)
        self.progress.advance()
        return(sorted(allMails,key=lambda subList:subList[self.MAILDATEID]))

    def makeId(self,fileName):
        thisId = re.sub(r".*/","",fileName)
        thisId = re.sub(r"\.xml.*$","",thisId)
        return(thisId)

    def processFile(self,patientFileName):
        tree = ET.parse(patientFileName)
        root = tree.getroot()
        thisId = self.makeId(patientFileName)
        return(self.getEmailData(root,thisId))

    def load(self):
        patientFileName = self.makeFileName(self.directory,self.patientId)
        mails = self.processFile(patientFileName)

        domain = self.corpusDomain(mails)
        table = Table.from_list(domain,mails)
        self.Outputs.data.send(Corpus.from_table(table.domain, table))

    def __init__(self):
        super().__init__()
        self.progress = gui.ProgressBar(self, 10)
        self.drawWindow()

if __name__ == "__main__":
    WidgetPreview(TactusLoader).run()
