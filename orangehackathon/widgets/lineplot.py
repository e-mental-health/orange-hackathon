import matplotlib.pyplot as plt
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
    storedTable = None
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
        columnNames = sorted([x.name for x in self.storedTable.domain.variables])
        form.addRow(
            "y:",
            gui.radioButtons(
                None, self, "yColumn",columnNames))
        form.addRow(gui.button(None, self, 'load', self.redraw))

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

    def drawGraph(self):
        data = []
        columnNames = sorted([x.name for x in self.storedTable.domain.variables])
        for i in range(0,len(self.storedTable)):
            data.append(self.getFieldValue(self.storedTable,columnNames[self.yColumn],i))
        self.plotId += 1
        plt.figure(self.plotId)
        plt.plot(data)
        plt.show()
