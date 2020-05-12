import sys
import os
from PyQt5.QtCore import QFile, QIODevice, QTextStream, QUrl, Qt, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from Orange.widgets.widget import OWWidget, Input
from Orange.widgets import gui
from Orange.data import Table

import pandas as pd
import json

from ..resources import resources

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
        # Convert Orange Table to Pandas DataFrame
        df = table_to_frame(self.storedTable, include_metas=True)
        print(df.columns)
        text = "beste@adj@compare@affect@posemo@drives@achieve@power@reward PER , bedankt voor@function@prep@adj@compare@relativ@time je@function@pronoun@ppron@you@social aanmelding . ik@function@pronoun@ppron@i heb@function@auxverb@verb@focuspresent de@function@article intake bekeken@verb@focuspast en@function@conj je@function@pronoun@ppron@you@social bent@function@auxverb@verb@focuspresent een@function@article geschikte kandidaat om@function@prep@conj te@function@prep@adverb starten met@function@prep de@function@article internetbehandeling LOC . binnen@function@prep@relativ@space NUM@number count werkdagen na@function@prep@adverb@adj@compare@relativ@time dit@function@pronoun@ipron bericht@social@drives@affiliation krijg je@function@pronoun@ppron@you@social een@function@article vaste hulpverlener toegewezen@verb@quant@cogproc@tentat@focuspast@work die@function@pronoun@ipron , om@function@prep@conj te@function@prep@adverb beginnen@verb@focuspast@focuspresent@relativ@time@work , uitgebreid@verb@cogproc@insight@focuspast@relativ@space op@function@prep@relativ@space je@function@pronoun@ppron@you@social intake zal@function@auxverb@verb@cogproc@discrep@focusfuture in@function@prep@relativ@space gaan@function@pronoun@verb@focuspresent@focusfuture@relativ@motion . ik@function@pronoun@ppron@i wens@verb@affect@posemo@cogproc@discrep@drives@reward@focuspresent@focusfuture je@function@pronoun@ppron@you@social veel@function@adverb@quant@cogproc succes@affect@posemo@drives@achieve@reward@work met@function@prep de@function@article behandeling@bio@health . met@function@prep vriendelijke groet@social@drives@affiliation , PER"
        html = self.transformMessage(text)
        self.view.setHtml(html)

    def getCatProp(self, cat, prop):
        return self.liwc_categories[self.liwc_categories["id"] == cat].iloc[0][prop]

    def getParentChain(self, cat):
        parent = self.cat_dict[cat]['parent']
        if parent == "root":
            return self.cat_dict[cat]['label']
        return self.getParentChain(parent) + " > " + self.cat_dict[cat]['label']

    def transformWord(self, taggedWord):
        split = taggedWord.split('@')
        
        # filter on selected categories
        liwc_cats = [cat for cat in split[1:] if self.tree_items[cat].checkState(0) == Qt.Checked]

        # filter on leaf nodes
        liwc_cats = filter(lambda cat: self.tree_items[cat].childCount() == 0, liwc_cats)
        
        annotations = [f'<div class="dot {cat} tooltip"><span class="tooltiptext">{self.getParentChain(cat)}</span></div>' for cat in liwc_cats]
        divs = "".join(annotations)
        return (f'<div class="nobr">{divs}<div class="tooltip"><span>{split[0]}</span>'
            f'<span class="tooltiptext">{", ".join(liwc_cats)}</span></div></div>&nbsp;&nbsp;&nbsp;')

    def transformMessage(self, taggedMessage):
        taggedWords = taggedMessage.split(' ')
        htmlMessage = ""
        for taggedWord in taggedWords:
            htmlMessage += self.transformWord(taggedWord)
        return f'<html>{htmlMessage}</html>'

    def loadLiwcCategories(self):
        tree = self.selectionTree
        self.liwc_categories = pd.read_csv(os.path.join(os.getcwd(), "orangehackathon", "widgets", "liwc_categories.csv"))
        tree.setHeaderLabels(['Category', 'Color'])
        tree.header().setStretchLastSection(False)
        tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        for index, row in self.liwc_categories.iterrows():
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
        # Load CSS template
        qurl = QUrl.fromLocalFile(os.getcwd() + "/orangehackathon/widgets/test.css")
        file = QtCore.QFile(qurl.toLocalFile())
        if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            return
        css = file.readAll().data().decode("utf-8")

        # Generate LIWC category colors
        s = ""
        for index, row in self.liwc_categories.iterrows():
            s += f".{row['id']} {{ background-color: {row['color']}; }}\n"
        css = css.replace('/* LIWC_COLORS */', s)
        print(css)

        # Set CSS
        self.view.loadCSS(css, "script1")
