import os
from PyQt5.QtCore import QIODevice, QTextStream, QUrl, Qt, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from Orange.widgets.widget import OWWidget, Input
from Orange.widgets import gui
from Orange.data import Table

import pandas as pd

from ..utils.pandas_compat import table_to_frame
from ..utils.webengineview import WebEngineView
from PyQt5.QtGui import QColor

class VisAnnotatedText(OWWidget):
    name = "Annotated text visualization"
    description = "Shows annotated texts in a viewer"
    icon = "icons/lineplot.svg"
    want_main_area = False
    storedTable = None

    class Inputs:
        table = Input("Data", Table)

    def __init__(self):
        super().__init__()
        self.layout = QBoxLayout(QBoxLayout.Direction.LeftToRight)

        self.tree_items = {} # dictionary for widget item lookup (liwc category -> tree widget item)
        self.cat_dict = {} # dictionary for faster lookup
        self.selectionTree = QTreeWidget()
        self.loadLiwcCategories()
        self.selectionTree.itemChanged.connect(self.redraw)
        self.layout.addWidget(self.selectionTree)

        self.view = WebEngineView()
        self.updateCSS()
        self.layout.addWidget(self.view)

        gui.widgetBox(self.controlArea, True, orientation=self.layout)

    @Inputs.table
    def storeTable(self,table):
        self.storedTable = table
        self.redraw()

    def redraw(self):
        if self.storedTable != None: self.draw()

    def draw(self):
        """ Generates and displays html for the provided data.
            The table is assumed to contain only one row.
        """
        df = table_to_frame(self.storedTable, include_metas=True)
        text = df.at[0, 'markedtext']
        html = self.transformMessage(text)
        self.view.setHtml(html)

    def getParentChain(self, cat):
        """ Helper function that generates the hierarchical path the specified LIWC category is in.
        """
        parent = self.cat_dict[cat]['parent']
        if parent == "root":
            return self.cat_dict[cat]['label']
        return self.getParentChain(parent) + " > " + self.cat_dict[cat]['label']

    def transformWord(self, annotatedWord):
        """ Transforms the annotated word into html with divs having classes corresponding
            to the annotations.
        """
        split = annotatedWord.split('@')

        # filter on selected categories
        liwc_cats = [cat for cat in split[1:] if self.tree_items[cat].checkState(0) == Qt.Checked]

        # filter on leaf nodes
        liwc_cats = filter(lambda cat: self.tree_items[cat].childCount() == 0, liwc_cats)

        annotations = [f'<div class="dot {cat} tooltip"><span class="tooltiptext">{self.getParentChain(cat)}</span></div>' for cat in liwc_cats]
        divs = "".join(annotations)
        return (f'<div class="nobr">{divs}<div class="tooltip"><span>{split[0]}</span>'
            f'<span class="tooltiptext">{", ".join(liwc_cats)}</span></div></div>&nbsp;&nbsp;&nbsp;')

    def transformMessage(self, annotatedMessage):
        """ Transforms the liwc-annotated message to html by separating the words and processing
            them separately. The annotated message should be formatted similar to this:
            "bedankt voor@function@prep@adj@compare@relativ@time je@function@pronoun@ppron@you@social aanmelding ."
        """
        annotatedWords = annotatedMessage.split(' ')
        htmlMessage = ""
        for annotatedWord in annotatedWords:
            htmlMessage += self.transformWord(annotatedWord)
        return f'<html>{htmlMessage}</html>'

    def loadLiwcCategories(self):
        """ Loads information about the LIWC categories (labels, colors, structure) from file.
        """
        tree = self.selectionTree
        self.liwc_categories = pd.read_csv(os.path.join(os.getcwd(),
            "orangehackathon", "widgets", "resources", "liwc_categories.csv"))
        tree.setHeaderLabels(['Category', 'Color'])
        tree.header().setStretchLastSection(False)
        tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        for _, row in self.liwc_categories.iterrows():
            parent_id = row['parent']
            parent = tree if parent_id == 'root' else self.tree_items[parent_id]
            item = QTreeWidgetItem(parent)
            item.setText(0, row['label'])
            item.setText(1, ' ')
            item.setBackground(1, QColor(row['color']))
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Checked)
            item.setExpanded(parent_id == 'root')
            self.tree_items[row['id']] = item
            self.cat_dict[row['id']] = {
                'parent': row['parent'],
                'label': row['label'],
                'color': row['color']
            }

    def updateCSS(self):
        """ Dynamically generates the CSS based on a template and the loaded LIWC features,
            which contains information about the colors to use.
        """
        # Load CSS template
        qurl = QUrl.fromLocalFile(os.path.join(os.getcwd(),
            "orangehackathon", "widgets", "resources", "liwc_style_template.css"))
        file = QtCore.QFile(qurl.toLocalFile())
        if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            return
        css = file.readAll().data().decode("utf-8")

        # Generate LIWC category colors
        s = ""
        for _, row in self.liwc_categories.iterrows():
            s += f".{row['id']} {{ background-color: {row['color']}; }}\n"
        css = css.replace('/* LIWC_COLORS */', s)

        # Set CSS
        self.view.loadCSS(css, "script1")
