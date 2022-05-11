import re
import sys
from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from   matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# alternatives: seaborn, plotnine, 
from PyQt5.QtCore import Qt,pyqtSignal
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
    SECONDSPERDAY = 86400
    WORDS = "words"
    MESSAGES = "messages"
    storedTable = None
    coloredColumn = -1
    xColumn = 0
    yColumn = 0
    connect = MESSAGES
    form = None
    ax = None

    class Inputs:
        table = Input("Data", Table)

    def __init__(self):
        super().__init__()
        self.form = QFormLayout()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.form.addWidget(self.canvas)
        self.form.setFieldGrowthPolicy(self.form.AllNonFixedFieldsGrow)
        self.form.setVerticalSpacing(0)
        self.form.setLabelAlignment(Qt.AlignLeft)
        gui.widgetBox(self.controlArea, True, orientation=self.form)

    @Inputs.table
    def storeTable(self,table):
        if table != None and hasattr(table, "domain"): 
            self.storedTable = table
            # 20191210 warning: reloading table may require replacing form
            # because set of features changed
            self.clearCanvas()
            self.drawGraph()
            self.drawWindow()

    def redraw(self):
        if self.storedTable != None: self.drawGraph()

    def drawGraph(self):
        self.clearCanvas()
        self.ax = self.figure.add_subplot(111)
        if self.connect == self.WORDS: self.plotWords()
        else: self.plotMessages()

    def drawWindow(self):
        form = self.form
        if self.storedTable == None : columnNames = []
        else: columnNames = [x.name for x in self.storedTable.domain.variables]
        if self.form.rowCount() <= 1:
            form.addRow("x-axis:",gui.comboBox(None, self, "xColumn",items=columnNames,callback=self.redraw))
            form.addRow("y-axis:",gui.comboBox(None, self, "yColumn",items=columnNames,callback=self.redraw))
            form.addRow("split by:",gui.comboBox(None, self, "coloredColumn",items=columnNames+[self.FIELDNAMENONE],callback=self.redraw))
            form.addRow("connect:",gui.comboBox(None, self, "connect",items=[self.MESSAGES,self.WORDS],callback=self.redraw))
            form.addRow(gui.button(None, self, 'draw', self.redraw))
            form.addRow(gui.button(None, self, 'clear', self.clearCanvas))

    def clearCanvas(self):
        #while self.form.rowCount() > 1: 
        #    print("deleting line plot row...")
        #    self.form.removeRow(1)
        self.figure.clear()
        self.figure.clf()
        self.canvas.draw()
        self.canvas.repaint()

    def getFieldValue(self,table,fieldName,rowId):
        if rowId < len(table):
            for i in range(0, len(table.domain.variables)):
                if table.domain[i].name == fieldName:
                    return(table[rowId].list[i])
            for i in range(0,len(table.domain.metas)):
                if table.domain.metas[i].name == fieldName:
                    return(table[rowId].metas[i])
        sys.exit("getFieldValue: field name not found: "+fieldName)

    def getColumnValues(self,table,columnName):
        return(list(set([self.getFieldValue(table,columnName,i) for i in range(0,len(table))])))

    def makeColorNames(self,columnName):
        columnValueList = sorted(self.getColumnValues(self.storedTable,columnName),reverse=True)
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

    def normalizeXvalues(self,xValues):
        for i in range(1,len(xValues)):
            xValues[i] -= xValues[0]
        xValues[0] = 0
        return(xValues)

    def convertSecondsToDays(self,xValues):
        return([x/self.SECONDSPERDAY for x in xValues])

    def plotWords(self):
        if self.storedTable == None or not hasattr(self.storedTable, "domain"): return
        columnNames = [x.name for x in self.storedTable.domain.variables]
        ax = self.ax
        ax.cla()
        lastMsgId = ""
        lastDataValue = None
        dataX = []
        dataY = []
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
        if len(dataX) > 0:
            ax.plot(dataX,dataY,color=color,label=lastDataValue)
            if self.coloredColumn >= 0 and self.coloredColumn < len(columnNames): 
                color = colorNames[lastDataValue]
            if len(dataX) > 1: ax.plot(dataX,dataY,color=color,label=lastDataValue)
            else: ax.scatter(dataX,dataY,color=color,label=lastDataValue)
        title = "x-axis: \""+columnNames[self.xColumn]+"\""+"; y-axis: \""+columnNames[self.yColumn]+"\""
        if self.coloredColumn >= 0 and self.coloredColumn < len(columnNames):
            title += "; color: \""+columnNames[self.coloredColumn]+"\""
            handlesUnique,labelsUnique = self.simplifyLegend(ax)
            ax.legend(handlesUnique,labelsUnique)
        ax.title.set_text(title)
        self.canvas.draw()
        self.canvas.repaint()

    def plotMessages(self):
        if self.storedTable == None or not hasattr(self.storedTable, "domain"): return
        columnNames = [x.name for x in self.storedTable.domain.variables]
        ax = self.ax
        ax.clear()
        self.fileName = str(self.getFieldValue(self.storedTable,self.FIELDNAMEFILE,0))
        xValues = self.normalizeXvalues([self.getFieldValue(self.storedTable,columnNames[self.xColumn],i) for i in range(0,len(self.storedTable))])
        if columnNames[self.xColumn] == self.FIELDNAMEDATE:
            xValues = self.convertSecondsToDays(xValues)
        if self.coloredColumn < 0 or self.coloredColumn >= len(columnNames):
            dataX = []
            dataY = []
            for i in range(0,len(self.storedTable)):
                newX = xValues[i]
                newY = self.getFieldValue(self.storedTable,columnNames[self.yColumn],i)
                dataX.append(newX)
                dataY.append(newY)
            if len(dataX) > 1: ax.plot(dataX,dataY,color=self.DEFAULTCOLOR)
            elif len(dataX) > 0: ax.scatter(dataX,dataY,color=self.DEFAULTCOLOR)
        else:
            colorNames = self.makeColorNames(columnNames[self.coloredColumn])
            columnValues = self.getColumnValues(self.storedTable,columnNames[self.coloredColumn])
            for columnValue in columnValues:
                dataX = []
                dataY = []
                for i in range(0,len(self.storedTable)):
                    dataValue = self.getFieldValue(self.storedTable,columnNames[self.coloredColumn],i)
                    if dataValue == columnValue: 
                        newX = xValues[i]
                        newY = self.getFieldValue(self.storedTable,columnNames[self.yColumn],i)
                        dataX.append(newX)
                        dataY.append(newY)
                if len(dataX) > 1: ax.plot(dataX,dataY,color=colorNames[columnValue],label=columnValue)
                elif len(dataX) > 0: ax.scatter(dataX,dataY,color=colorNames[columnValue],label=columnValue)
        title = "x-axis: \""+columnNames[self.xColumn]+"\""+"; y-axis: \""+columnNames[self.yColumn]+"\""
        if self.coloredColumn >= 0 and self.coloredColumn < len(columnNames):
            title += "; color: \""+columnNames[self.coloredColumn]+"\""
            handlesUnique,labelsUnique = self.simplifyLegend(ax)
            ax.legend(handlesUnique,labelsUnique)
        ax.title.set_text(title)
        self.canvas.draw()
        self.canvas.repaint()

