from PyQt5.QtCore import QFile, QIODevice, QTextStream
from PyQt5.QtWidgets import QFormLayout
from Orange.widgets.widget import OWWidget, Input
from Orange.widgets import gui
from Orange.data import Table

import altair as alt
import json

from ..resources import resources

from ..utils.pandas_compat import table_to_frame
from ..utils.webengineview import WebEngineView

class VisConversation(OWWidget):
    name = "Conversation visualization"
    description = "Visualization of conversations on a timeline"
    icon = "icons/lineplot.svg"
    want_main_area = False
    DAAP = "daap"
    COLORPREFIX = "C"
    DEFAULTCOLOR = COLORPREFIX+"0"
    storedTable = None

    class Inputs:
        table = Input("Data", Table)

    def __init__(self):
        super().__init__()
        self.form = QFormLayout()

        # Read file from QT resources
        stream = QFile(':vegaspec-conversation-overview.json')
        stream.open(QIODevice.ReadOnly)
        if not stream.exists():
            raise Exception('Vega spec not found')
        text = QTextStream(stream).readAll()
        stream.close()

        # Load vega-spec json file into a dictionary
        self.dict = json.loads(text)

        # Create the Altair chart
        self.chart = alt.Chart.from_dict(self.dict)

        # Show the chart in a WebEngineView
        self.view = WebEngineView()
        self.form.addWidget(self.view)
        self.view.updateChart(self.chart)

        gui.widgetBox(self.controlArea, True, orientation=self.form)

    @Inputs.table
    def storeTable(self,table):
        if table != None:
            self.storedTable = table

            # Convert Orange Table to Pandas DataFrame
            df = table_to_frame(table, include_metas=True)

            # Convert Pandas DataFrame to CSV
            csv = df.to_csv()

            # Store data in Vega dictionary
            self.dict['data']['values'] = csv

            # Update (recreate) the chart
            self.chart = alt.Chart.from_dict(self.dict)
            self.view.updateChart(self.chart)


    def redraw(self):
        if self.storedTable != None: self.drawGraph()

    def drawGraph(self):
        pass
