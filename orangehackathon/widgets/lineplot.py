import re
import sys
import matplotlib.pyplot as plt
# alternatives: seaborn, plotnine, 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout
from Orange.widgets.widget import OWWidget, Input
from Orange.widgets import gui
from Orange.data import Table, Domain
from Orange.widgets.utils.itemmodels import DomainModel

class LinePlot(OWWidget):
    name = "Line Plot"
    description = "Make a line plot of data"
    icon = "icons/lineplot.svg"
    want_main_area = False
    DAAP = "daap"
    COLORPREFIX = "C"
    DEFAULTCOLOR = COLORPREFIX+"0"
    FIELDNAMEDATE = "date"
    FIELDNAMENONE = "NONE"
    FIELDNAMEMSGID = "msg id"
    FIELDNAMEFILE = "file"
    WORDS = "words"
    MESSAGES = "messages"
    storedTable = None
    coloredColumn = -1
    fileName = ""
    plotId = 0
    xColumn = 0
    yColumn = 0
    connect = MESSAGES

    class Inputs:
        table = Input("Data", Table)

    def __init__(self):
        super().__init__()
        self.label = gui.widgetLabel(self.controlArea)
        self.progress = gui.ProgressBar(self, 10)

    def redraw(self):
        if self.storedTable != None: self.drawGraph()

    def drawWindow(self):
        form = QFormLayout()
        form.setFieldGrowthPolicy(form.AllNonFixedFieldsGrow)
        form.setVerticalSpacing(0)
        form.setLabelAlignment(Qt.AlignLeft)
        gui.widgetBox(self.controlArea, True, orientation=form)
        if self.storedTable == None: columnNames = []
        else: columnNames = [x.name for x in self.storedTable.domain.variables]
        form.addRow("x-axis:",
                gui.comboBox(None, self, "xColumn",items=columnNames))
        form.addRow("y-axis:",
                gui.comboBox(None, self, "yColumn",items=columnNames))
        form.addRow("color:",
                gui.comboBox(None, self, "coloredColumn",items=columnNames+[self.FIELDNAMENONE]))
        form.addRow("connect:",
                gui.comboBox(None, self, "connect",items=[self.MESSAGES,self.WORDS]))
        form.addRow(gui.button(None, self, 'draw', self.redraw))

    def getFieldValue(self,table,fieldName,rowId):
        if rowId < len(table):
            for i in range(0,len(table.domain)):
                if table.domain[i].name == fieldName:
                    return(table[rowId].list[i])
            for i in range(0,len(table.domain.metas)):
                if table.domain.metas[i].name == fieldName:
                    return(table[rowId].metas[i])
        sys.exit("getFieldValue: field name not found: "+fieldName)

    @Inputs.table
    def storeTable(self,table):
        if table != None: 
            self.storedTable = table
            self.drawWindow()
            self.drawGraph()

    def getColumnValues(self,table,columnName):
        return(list(set([self.getFieldValue(table,columnName,i) for i in range(0,len(table))])))

    def makeColorNames(self,columnName):
        columnValueList = self.getColumnValues(self.storedTable,columnName)
        colorNames = {}
        for i in range(0,len(columnValueList)):
            colorNames[columnValueList[i]] = self.COLORPREFIX+str(i % 10)
        return(colorNames)

    def simplifyLegend(self,ax):
        handles, labels = ax.get_legend_handles_labels()
        nbrOfUniqueLabels = len(set(labels))
        handlesUnique = []
        labelsUnique = []
        seen = {}
        for i in range(0,len(labels)):
            if not labels[i] in seen:
                seen[labels[i]] = True
                labelsUnique.append(labels[i])
                handlesUnique.append(handles[i])
                if len(labelsUnique) >= nbrOfUniqueLabels: break
        return(handlesUnique,labelsUnique)

    def mixSorted(self,thisList):
        strList = []
        numList = []
        for i in range(0,len(thisList)):
            if re.match("^\d+$",thisList[i]): numList.append(int(thisList[i]))
            else: strList.append(thisList[i])
        return(sorted(strList)+[str(x) for x in sorted(numList)])

    def plotWords(self):
        OWWidget.progressBarInit(self)
        columnNames = [x.name for x in self.storedTable.domain.variables]
        self.plotId += 1
        plt.figure(self.plotId)
        ax = plt.subplot(111)
        lastMsgId = ""
        lastDataValue = None
        dataX = []
        dataY = []
        self.progress.iter = len(self.storedTable)
        color = self.DEFAULTCOLOR
        if self.coloredColumn >= 0 and self.coloredColumn < len(columnNames):
            colorNames = self.makeColorNames(columnNames[self.coloredColumn])
        for i in range(0,len(self.storedTable)):
            currentMsgId = self.getFieldValue(self.storedTable,self.FIELDNAMEMSGID,i)
            newX = self.getFieldValue(self.storedTable,columnNames[self.xColumn],i)
            newY = self.getFieldValue(self.storedTable,columnNames[self.yColumn],i)
            if i > 0 and currentMsgId != lastMsgId and self.connect != self.WORDS:
                ax.plot([dataX[-1],newX],[dataY[-1],newY],color=self.DEFAULTCOLOR,label=lastDataValue)
            if currentMsgId != lastMsgId and len(dataX) > 0:
                if self.coloredColumn >= 0 and self.coloredColumn < len(columnNames):
                    color = colorNames[lastDataValue]
                ax.plot(dataX,dataY,color=color,label=lastDataValue)
                dataX = []
                dataY = []
            dataX.append(newX)
            dataY.append(newY)
            lastMsgId = currentMsgId
            lastDataValue = self.getFieldValue(self.storedTable,columnNames[self.coloredColumn],i)
            self.progress.advance()
        if len(dataX) > 0:
            ax.plot(dataX,dataY,color=color,label=lastDataValue)
            if self.coloredColumn >= 0 and self.coloredColumn < len(columnNames): 
                color = colorNames[lastDataValue]
            plt.plot(dataX,dataY,color=color,label=lastDataValue)
        title = "file: "+self.fileName+"; x-axis: \""+columnNames[self.xColumn]+"\""+"; y-axis: \""+columnNames[self.yColumn]+"\""
        if self.coloredColumn >= 0 and self.coloredColumn < len(columnNames):
            title += "; color: \""+columnNames[self.coloredColumn]+"\""
            handlesUnique,labelsUnique = self.simplifyLegend(ax)
            ax.legend(handlesUnique,labelsUnique)
        plt.title(title)
        plt.show()

    def plotMessages(self):
        OWWidget.progressBarInit(self)
        columnNames = [x.name for x in self.storedTable.domain.variables]
        self.plotId += 1
        plt.figure(self.plotId)
        ax = plt.subplot(111)
        self.progress.iter = len(self.storedTable)
        self.fileName = str(self.getFieldValue(self.storedTable,self.FIELDNAMEFILE,0))
        if self.coloredColumn < 0 or self.coloredColumn >= len(columnNames):
            dataX = []
            dataY = []
            for i in range(0,len(self.storedTable)):
                newX = self.getFieldValue(self.storedTable,columnNames[self.xColumn],i)
                newY = self.getFieldValue(self.storedTable,columnNames[self.yColumn],i)
                dataX.append(newX)
                dataY.append(newY)
            ax.plot(dataX,dataY,color=self.DEFAULTCOLOR)
        else:
            colorNames = self.makeColorNames(columnNames[self.coloredColumn])
            columnValues = self.getColumnValues(self.storedTable,columnNames[self.coloredColumn])
            for columnValue in columnValues:
                dataX = []
                dataY = []
                for i in range(0,len(self.storedTable)):
                    dataValue = self.getFieldValue(self.storedTable,columnNames[self.coloredColumn],i)
                    if dataValue == columnValue: 
                        newX = self.getFieldValue(self.storedTable,columnNames[self.xColumn],i)
                        newY = self.getFieldValue(self.storedTable,columnNames[self.yColumn],i)
                        dataX.append(newX)
                        dataY.append(newY)
                    if len(dataX) > 0: ax.plot(dataX,dataY,color=colorNames[columnValue],label=columnValue)
        title = "file: "+self.fileName+"; x-axis: \""+columnNames[self.xColumn]+"\""+"; y-axis: \""+columnNames[self.yColumn]+"\""
        if self.coloredColumn >= 0 and self.coloredColumn < len(columnNames):
            title += "; color: \""+columnNames[self.coloredColumn]+"\""
            handlesUnique,labelsUnique = self.simplifyLegend(ax)
            ax.legend(handlesUnique,labelsUnique)
        plt.title(title)
        plt.show()

    def drawGraph(self):
        if self.connect == self.WORDS: self.plotWords()
        else: self.plotMessages()
