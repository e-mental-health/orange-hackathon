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

import datetime as dt

class SortEmails(OWWidget):
    name = "Sort Emails"
    description = "Sort emails based on date"
    icon = "icons/sort-icon.svg"
    
    filter_asc = Setting(1)
    date_format = "%Y-%m-%d %H:%M:%S"
    corpus = None
    
    class Inputs:
        in_channel = Input("Corpus in", Corpus)
    
    class Outputs:
        out_channel = Output("Corpus out", Corpus)
    
    def __init__(self):
        super().__init__()
        
        self.label = gui.widgetLabel(self.controlArea)
        self.optionsBox = gui.widgetBox(self.controlArea, "Options")
        gui.checkBox(self.optionsBox, self, 'filter_asc', "Filter in ascending order")
        gui.button(self.optionsBox, self, "Filter", callback=self.process_channel)
        
    def filterEmails(self, corpus):
        date_key = "date"
        try:
            if isinstance(corpus[0][date_key].value, float):
                sort_key = lambda x: corpus[x][date_key].value
            else:
                sort_key = lambda x: dt.datetime.strptime(corpus[x][date_key].value, self.date_format)

            new_index = sorted(range(corpus.metas.shape[0]), key=sort_key)
            if not self.filter_asc:
                new_index.reverse()
            corpus.metas = corpus.metas[new_index]
        except ValueError:  # no date_key in corpus
            print(f"[Module {self.name}] Error: no column called {date_key}")
        
        return corpus
    
    @Inputs.in_channel
    def process_channel(self, corpus):
        if corpus:
            self.corpus = corpus
        if not corpus and self.corpus:
            corpus = self.corpus
    
        if corpus:
            print(f"[Module: {self.name}] Processing emails")
            corpus = self.filterEmails(corpus)                       
            self.Outputs.out_channel.send(corpus)
        else:
            print(f"[Module: {self.name}] Getting empty corpus")
        
    