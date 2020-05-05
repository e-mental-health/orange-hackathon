from Orange.data import Table, Domain
from Orange.data import TimeVariable, ContinuousVariable, DiscreteVariable, StringVariable

import gzip
import numpy as np
import os
import re
import xml.etree.ElementTree as ET

DEFAULTDIRECTORY = "/home/erikt/projects/e-mental-health/usb/releases/20191217"
DEFAULTPATIENTID = 1
COUNSELORIDTAG = "./AssignedCounselor"
MESSAGETAG = "./Messages/Message"
SENDER = "Sender"
RECIPIENT = "Recipients"
SENDER = "Sender"
SUBJECT = "Subject"
BODY = "Body"
DATESENT = "DateSent"
CLIENT = "CLIENT"
COUNSELOR = "COUNSELOR"
FIELDDATE = "date"
FIELDFROM = "from"
FIELDTO = "to"
FIELDFILE = "file"
FIELDCOUNSELOR = "counselor"
FIELDSUBJECT = "subject"
FIELDTEXT = "text"
MAILDATEID = 3
MAILBODYID = 5
MAXIDLEN = 4
INFILEPREFIX = "AdB"
INFILESUFFIX = "-an.xml"
QUESTIONMARK = "?"

def corpusDomain(mails):
    return(Domain([TimeVariable.make(FIELDDATE),                              \
                   DiscreteVariable.make(FIELDFROM,set([x[1] for x in mails])),  \
                   DiscreteVariable.make(FIELDTO,set([x[2] for x in mails]))], \
            metas=[StringVariable.make(FIELDTEXT),                            \
                   StringVariable.make(FIELDFILE),                            \
                   StringVariable.make(FIELDCOUNSELOR),                       \
                   StringVariable.make(FIELDSUBJECT)]))

def makeFileName(patientId):
    if patientId == "": patientId = DEFAULTPATIENTID
    fileName = str(patientId)
    while (len(fileName) < MAXIDLEN): fileName = "0"+fileName
    return(INFILEPREFIX+fileName+INFILESUFFIX)

def sentenceSplit(text):
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

def cleanupMails(clientMails, counselorMails):
    clientSentenceDates = {}
    counselorSentenceDates = {}
    for i in range(0,len(clientMails)):
        date = clientMails[i][MAILDATEID]
        body = clientMails[i][MAILBODYID]
        sentences = sentenceSplit(body)
        for s in sentences:
            if (s in clientSentenceDates and date < clientSentenceDates[s]) or \
                not s in clientSentenceDates:
                clientSentenceDates[s] = date
    for i in range(0,len(counselorMails)):
        date = counselorMails[i][MAILDATEID]
        body = counselorMails[i][MAILBODYID]
        sentences = sentenceSplit(body)
        for s in sentences:
            if s in clientSentenceDates and date < clientSentenceDates[s]:
                counselorSentenceDates[s] = date
                del(clientSentenceDates[s])
            elif s in counselorSentenceDates and date < counselorSentenceDates[s]:
                counselorSentenceDates[s] = date
            elif not s in clientSentenceDates and not s in counselorSentenceDates:
                counselorSentenceDates[s] = date
    for i in range(0,len(clientMails)):
        date = clientMails[i][MAILDATEID]
        body = clientMails[i][MAILBODYID]
    return(clientMails)

def cleanupText(text):
    if text == None: return("")
    text = re.sub(r"\s+"," ",text)
    text = re.sub(r"^ ","",text)
    text = re.sub(r" $","",text)
    return(text)

def anonymizeCounselor(name):
    if name != CLIENT: return(COUNSELOR)
    else: return(name)

def getEmailData(root,patientFileName,counselorId):
    clientMails = []
    counselorMails = []
    for message in root.findall(MESSAGETAG):
        body = ""
        date = ""
        recipient = ""
        sender = ""
        subject = ""
        for child in message:
            if child.tag == SENDER: 
                sender = anonymizeCounselor(cleanupText(child.text))
            elif child.tag == RECIPIENT: 
                recipient = anonymizeCounselor(cleanupText(child.text))
            elif child.tag == DATESENT: date = cleanupText(child.text)
            elif child.tag == SUBJECT: subject = cleanupText(child.text)
            elif child.tag == BODY: body = cleanupText(child.text)
        if sender == CLIENT: clientMails.append([date,sender,recipient,body,patientFileName,counselorId,subject])
        else: counselorMails.append([date,sender,recipient,body,patientFileName,counselorId,subject])
    clientMails = cleanupMails(clientMails,counselorMails)
    counselorMails = cleanupMails(counselorMails,clientMails)
    allMails = clientMails
    allMails.extend(counselorMails)
    return(sorted(allMails,key=lambda subList:subList[MAILDATEID]))

def getCounselorId(root):
    counselorId = ""
    for counselorIdTag in root.findall(COUNSELORIDTAG):
        if counselorIdTag.text != None: counselorId = counselorIdTag.text
        break
    return(counselorId)

def mails2table(mails):
    domain = corpusDomain(mails)
    table = Table.from_list(domain,mails) # replaces "" in cells with "?"
    return(table)

def processFile(directory,patientFileName):
    if directory == "": directory = DEFAULTDIRECTORY
    try:
        if re.match(r"^.*\.gz$",patientFileName):
            with gzip.open(directory+"/"+patientFileName,"rb") as f: text = f.read()
            root = ET.fromstring(text)
        else:
            try:
                tree = ET.parse(directory+"/"+patientFileName)
                root = tree.getroot()
            except:
                with gzip.open(directory+"/"+patientFileName+".gz","rb") as f: text = f.read()
                root = ET.fromstring(text)
        counselorId = getCounselorId(root)
        mails = getEmailData(root,patientFileName,counselorId)
        table = mails2table(mails)
        return(table,mails)
    except:
        print("File processing error:",directory+"/"+patientFileName)
        return([],[])

if __name__ == "__main__":
    pass
