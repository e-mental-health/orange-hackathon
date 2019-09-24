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
    DEFAULTCOLOR = "C0"
    storedTable = None
    coloredColumn = -1
    plotId = 0
    xColumn = 0
    yColumn = 0

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
        else: columnNames = sorted([x.name for x in self.storedTable.domain.variables])
        form.addRow("x-axis:",
            gui.radioButtons(None, self, "xColumn",columnNames))
        form.addRow("y-axis:",
            gui.radioButtons(None, self, "yColumn",columnNames))
        form.addRow("color:",
            gui.radioButtons(None, self, "coloredColumn",columnNames+[self.FIELDNAMENONE]))
        form.addRow(gui.button(None, self, 'draw', self.redraw))

    def getFieldValue(self,table,fieldName,rowId):
        for i in range(0,len(table.domain)):
            if table.domain[i].name == fieldName:
                return(table[rowId].list[i])
        sys.exit("getFieldValue: field name not found: "+fieldName)

    @Inputs.table
    def storeTable(self,table):
        if table != None: 
            self.storedTable = table
            self.drawWindow()
            self.drawGraph()

    def makeColorNames(self,columnName):
        columnValueList = list(set([self.getFieldValue(self.storedTable,columnName,i) for i in range(0,len(self.storedTable))]))
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

    def drawGraph(self):
        OWWidget.progressBarInit(self)
        columnNames = sorted([x.name for x in self.storedTable.domain.variables])
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
            if currentMsgId != lastMsgId and len(dataX) > 0:
                if self.coloredColumn >= 0 and self.coloredColumn < len(columnNames):
                    color = colorNames[lastDataValue]
                ax.plot(dataX,dataY,color=color,label=lastDataValue)
                dataX = []
                dataY = []
            dataX.append(self.getFieldValue(self.storedTable,columnNames[self.xColumn],i))
            dataY.append(self.getFieldValue(self.storedTable,columnNames[self.yColumn],i))
            lastMsgId = currentMsgId
            lastDataValue = self.getFieldValue(self.storedTable,columnNames[self.coloredColumn],i)
            self.progress.advance()
        if len(dataX) > 0:
            if self.coloredColumn >= 0 and self.coloredColumn < len(columnNames): 
                color = colorNames[lastDataValue]
            plt.plot(dataX,dataY,color=color,label=lastDataValue)
        title = "x-axis: \""+columnNames[self.xColumn]+"\""+"; y-axis: \""+columnNames[self.yColumn]
        if self.coloredColumn >= 0 and self.coloredColumn < len(columnNames):
            title += "\"; color: \""+columnNames[self.coloredColumn]+"\""
            handlesUnique,labelsUnique = self.simplifyLegend(ax)
            ax.legend(handlesUnique,labelsUnique)
        plt.title(title)
        plt.show()
