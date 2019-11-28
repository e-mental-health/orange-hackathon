#!/usr/bin/env python
"""

/home/tyler/Documents/Hackaton/enron_mail_20150507/maildir/symes-k


    Sort widget for Orange
    Sorts a corpus with a date column
    By David Brouwer
    david.brouwer.99@gmail.com
    https://github.com/Davincible

    TODO:
    - only works with date key word,
        check if date key word is in the corpus and give feedback to the user in the gui about that
    - create a dropdown with all the columns, so the user can manually select the date column, defaulting to "date"

"""
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets.settings import Setting
from Orange.widgets import gui
from orangecontrib.text.corpus import Corpus
import orangehackathon.libs.OWEmailSorterLIB as OWEmailSorterLIB

class SortEmails(OWWidget):
    name = "Sort Emails"
    description = "Sort emails based on date"
    icon = "icons/sort-icon.svg"

    filter_asc = Setting(1)
    corpus = None

    class Inputs:
        in_channel = Input("Corpus", Corpus)

    class Outputs:
        out_channel = Output("Corpus", Corpus)

    def __init__(self):
        super().__init__()

        self.label = gui.widgetLabel(self.controlArea)
        self.optionsBox = gui.widgetBox(self.controlArea, "Options")
        gui.checkBox(self.optionsBox, self, 'filter_asc', "Filter in ascending order")
        gui.button(self.optionsBox, self, "Filter", callback=self.process_channel)

    @Inputs.in_channel
    def process_channel(self, corpus):
        if corpus:
            self.corpus = corpus
        if not corpus and self.corpus:
            corpus = self.corpus

        if corpus:
            corpus = OWEmailSorterLIB.filterEmails(corpus,filter_asc=self.filter_asc)
            self.Outputs.out_channel.send(corpus)
        else:
            print(f"[Module: {self.name}] Warning: empty corpus")
