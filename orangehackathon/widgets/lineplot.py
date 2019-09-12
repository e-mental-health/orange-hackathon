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
    FIELDNAMEMSGID = "msg id"
    DEFAULTCOLOR = "C0"
    storedTable = None
    coloredColumn = -1
    plotId = 0
    yColumn = 0

    class Inputs:
        table = Input("Data", Table)

    def drawWindow(self):
        form = QFormLayout()
        form.setFieldGrowthPolicy(form.AllNonFixedFieldsGrow)
        form.setVerticalSpacing(0)
        form.setLabelAlignment(Qt.AlignLeft)
        gui.widgetBox(self.controlArea, True, orientation=form)
        if self.storedTable == None: columnNames = []
        else: columnNames = sorted([x.name for x in self.storedTable.domain.variables])
        form.addRow(
            "y-axis:",
            gui.radioButtons(
                None, self, "yColumn",columnNames))
        form.addRow(
            "class:",
            gui.radioButtons(
                None, self, "coloredColumn",columnNames))
        form.addRow(gui.button(None, self, 'draw', self.redraw))

    def __init__(self):
        super().__init__()
        self.label = gui.widgetLabel(self.controlArea)

    def getFieldValue(self,table,fieldName,rowId):
        for i in range(0,len(table.domain)):
            if table.domain[i].name == fieldName:
                return(table[rowId].list[i])
        sys.exit("getFieldValue: field name not found: "+fieldName)

    def redraw(self):
        if self.storedTable != None: self.drawGraph()

    @Inputs.table
    def storeTable(self,table):
        if table != None: 
            self.storedTable = table
            self.drawWindow()
            self.drawGraph()

    def makeColorName(self,columnName=None,columnValue=None):
        if columnValue == None: return(self.DEFAULTCOLOR)
        else:
            columnValueList = list(set([self.getFieldValue(self.storedTable,columnName,i) for i in range(0,len(self.storedTable))]))
            columnValueIndex = [i for i in range(0,len(columnValueList)) if columnValueList[i] == columnValue][0]
            columnValueIndex = columnValueIndex % 10
            return(self.COLORPREFIX+str(columnValueIndex))

    def simplifyLegend(self,ax):
        handles, labels = ax.get_legend_handles_labels()
        handlesUnique = []
        labelsUnique = []
        seen = {}
        for i in range(0,len(labels)):
            if not labels[i] in seen:
                seen[labels[i]] = True
                labelsUnique.append(labels[i])
                handlesUnique.append(handles[i])
        return(handlesUnique,labelsUnique)

    def drawGraph(self):
        columnNames = sorted([x.name for x in self.storedTable.domain.variables])
        self.plotId += 1
        plt.figure(self.plotId)
        if self.coloredColumn < 0: 
            lastMsgId = -1
            dataX = []
            dataY = []
            for i in range(0,len(self.storedTable)):
                currentMsgId = self.getFieldValue(self.storedTable,self.FIELDNAMEMSGID,i)
                if currentMsgId != lastMsgId and len(dataX) > 0:
                    plt.plot(dataX,dataY,color=self.makeColorName())
                    dataX = []
                    dataY = []
                dataX.append(i)
                dataY.append(self.getFieldValue(self.storedTable,columnNames[self.yColumn],i))
                lastMsgId = currentMsgId
            if len(dataX) > 0: 
                plt.plot(dataX,dataY,color=self.makeColorName())
            plt.title("y-axis: \""+columnNames[self.yColumn]+"\"")
        else:
            ax = plt.subplot(111)
            lastMsgId = ""
            lastDataValue = None
            dataX = []
            dataY = []
            for i in range(0,len(self.storedTable)):
                currentMsgId = self.getFieldValue(self.storedTable,self.FIELDNAMEMSGID,i)
                if currentMsgId != lastMsgId and len(dataX) > 0:
                    ax.plot(dataX,dataY,color=self.makeColorName(columnNames[self.coloredColumn],lastDataValue),label=lastDataValue)
                    dataX = []
                    dataY = []
                dataX.append(i)
                dataY.append(self.getFieldValue(self.storedTable,columnNames[self.yColumn],i))
                lastMsgId = currentMsgId
                lastDataValue = self.getFieldValue(self.storedTable,columnNames[self.coloredColumn],i)
            if len(dataX) > 0:
                plt.plot(dataX,dataY,color=self.makeColorName(columnNames[self.coloredColumn],lastDataValue),label=lastDataValue)
            handlesUnique,labelsUnique = self.simplifyLegend(ax)
            ax.legend(handlesUnique,labelsUnique)
            plt.title("y-axis: \""+columnNames[self.yColumn]+"\"; class: \""+columnNames[self.coloredColumn]+"\"")
        plt.show()
