#!/usr/bin/env python
"""
    Orange3 widget to convert mail files to tsv files, such that they can be used as a corpus

    By David Brouwer
    david.brouwer.99@gmail.com
    https://github.com/Davincible
    
    TODO:
     - implement threading as explained in : https://docs.biolab.si//3/development/tutorial-responsive-gui.html

"""
from Orange.widgets.widget import OWWidget, Output
from Orange.widgets.settings import Setting
from Orange.widgets import gui
from orangecontrib.text.corpus import Corpus
from orangehackathon.utils.mail2tsv import openStdoutAsCsv, mail2tsv
from AnyQt.QtWidgets import QGridLayout, QLabel
from AnyQt.QtCore import Qt
from pathlib import Path
from os.path import exists
import os
import json


class MailTsv(OWWidget):
    name = "Mail2Tsv"
    description = "Convert raw e-mail files to tsv files, extracting all important information"
    icon = "icons/sort-icon.svg"
    priority = 1010
    
    input_directory = ""
    output_directory = ""
    output_file = "mailOutput.tsv"
    enable_filter = Setting(True)
    filter_directories = "all_documents/, inbox/"
    valid_path = False  # flag to keep track if valid path is specified by user
    progress = None  # progress widget

    class Outputs:
        out_channel = Output("Corpus out", Corpus)

    def __init__(self):
        super().__init__()
        self._load_settings()
        self.create_gui()
        
    def create_gui(self):
        """ create the GUI """
        gui.label(self.controlArea, self,
                  "All files in the selected directory and subsequent subdirectories will be included in the conversion,"
                  "\nand output in a single .tsv file")
        gui.separator(self.controlArea, height=16)
        statusBox = gui.widgetBox(self.controlArea, "Status")
        inputBox = gui.vBox(self.controlArea, "Input")
        outputBox = gui.widgetBox(self.controlArea, "Output")

        self.statusLabel = gui.label(statusBox, self, "Select directories, and press process to start")

        # input GUI
        layout = QGridLayout()
        gui.widgetBox(inputBox, margin=0, orientation=layout)
        label = QLabel("Directory:")
        lineEdit = gui.lineEdit(None, self, "input_directory",
                                orientation=Qt.Horizontal,
                                tooltip="Tooltip",
                                placeholderText="input directory")
        layout.addWidget(label, 0, 1)
        layout.addWidget(lineEdit, 0, 2)

        checkbox = gui.checkBox(None, self, 'enable_filter', "Enable filter")
        layout.addWidget(checkbox, 2, 1)
        layout.addWidget(QLabel("Only include files from the subdirectories:"), 2, 2)
        filter = gui.lineEdit(None, self, "filter_directories",
                                 orientation=Qt.AlignLeft,
                                 tooltip="Tooltip",
                                 placeholderText="filter directories")
        layout.addWidget(filter, 2, 3)

        # output GUI
        layout2 = QGridLayout()
        gui.widgetBox(outputBox, margin=0, orientation=layout2)
        label2 = QLabel("Output directory:")
        lineEdit2 = gui.lineEdit(None, self, "output_directory",
                                 orientation=Qt.AlignLeft,
                                 tooltip="Tooltip",
                                 placeholderText="input directory")
        label3 = QLabel("Output file:")
        lineEdit3 = gui.lineEdit(None, self, "output_file",
                                 orientation=Qt.Horizontal,
                                 tooltip="Tooltip",
                                 placeholderText="input directory")

        layout2.addWidget(label2, 0, 1)
        layout2.addWidget(lineEdit2, 0, 2)
        layout2.addWidget(label3, 1, 1)
        layout2.addWidget(lineEdit3, 1, 2)

        # Process button
        layout3 = QGridLayout()
        gui.widgetBox(self.controlArea, margin=0, orientation=layout3)
        btn1 = gui.button(None, self, "Process", callback=self.process)
        btn2 = gui.button(None, self, "Output file > corpus", callback=self.output_corpus)
        layout3.addWidget(btn1, 0, 0)
        layout3.addWidget(btn2, 0, 1)

    def _load_settings(self, path="mail-tsv-settings.json"):
        """ load the input settings """
        path = str(Path.joinpath(Path.home(), '.orange/' + path))
        if exists(path):
            with open(path, 'r') as file:
                settings = json.load(file)

                self.input_directory = settings['input_directory']
                self.output_directory = settings['output_directory']
                self.output_file = settings['output_file']
                self.filter_directories = settings['filter_dirs']

    def _save_settings(self, path="mail-tsv-settings.json"):
        """ save the input settings """
        settings = {"input_directory": self.input_directory.strip(),
                    "output_directory": self.output_directory.strip(),
                    "output_file": self.output_file.strip(),
                    "filter_dirs": self.filter_directories.strip()}

        home = Path.joinpath(Path.home(), '.orange')
        if not Path.exists(home):
            Path.mkdir(home)

        path = str(Path.joinpath(home, path))
        with open(path, 'w') as file:
            json.dump(settings, file)

    def check_paths(self):
        """ Validate if user paths exist """
        text = msg = ""
        valid_input = valid_output = True

        # validate input directories
        if not exists(self.input_directory):
            text += "\nInvalid input directory"
            valid_input = False
        if not exists(self.output_directory):
            text += "\nInvalid output directory"
            valid_output = False
        if text:
            self.statusLabel.setText(text.strip())

        # check which directories are invalid, and adapt message accordingly
        if not valid_input and not valid_output:
            msg = "input & output"
        elif not valid_input:
            msg = "input"
        elif not valid_output:
            msg = "output"

        self.valid_path = valid_input & valid_output
        self.warning(f"Invalid {msg} directory", shown=not self.valid_path)

    def clean_data(self):
        """ clean user data """
        self.input_directory = self.input_directory.strip()
        self.output_directory = self.output_directory.strip()
        self.output_file = self.output_file.strip()
        self.filter_directories = self.filter_directories.strip()

    def convert(self):
        """ convert the mail files to tsv using the mail2tsv script in the utils folder """
        files = []
        self.statusLabel.setText("Loading file names...")
        self.progress = gui.ProgressBar(self, 100)
        self.progress.advance(0)

        # get all sub-directories with files
        walk = os.walk(self.input_directory)
        if self.enable_filter:
            filters = list(map(lambda x: str.strip(x, '\\/ '), self.filter_directories.split(',')))
            walk = list(filter(lambda x: x[0].split('/')[-1] in filters, walk))

        # add files to list
        for folder in walk:
            new_files = map(lambda x: os.path.join(folder[0], x), folder[2])
            files.extend(new_files)
        self.progress.iter = len(files)

        # convert files
        out_path = os.path.join(self.output_directory, self.output_file)
        csvwriter, file_obj = openStdoutAsCsv(out_path)
        index, errors = 1, 0
        print(f"[Module: {self.name}   ] converting {len(files)} files")
        for file in files:
            try:
                # print("file is :", file)
                mail2tsv(file, csvwriter, index, self.input_directory)
                index += 1
                self.progress.advance()
                num_files = len(files)
                self.statusLabel.setText(f"Processing file {index}/{num_files}")
            except Exception as e:
                print(f"[Module: {self.name}   ] failed processing {file} with error {e}")
                errors += 1

        # close output file
        if file_obj:
            file_obj.close()

        # give status back to user
        msg = "Finished converting files"
        if errors:
            msg += f" with {errors} error(s), please check terminal for details"
        self.statusLabel.setText(msg)
        self.progress.advance()
        self.progress.finish()

    def output_corpus(self):
        out_file = os.path.join(self.output_directory, self.output_file)
        if exists(out_file):
            corpus = Corpus.from_file(out_file)
            self.Outputs.out_channel.send(corpus)

    def process(self):
        self.clean_data()
        self._save_settings()
        self.check_paths()
        if self.valid_path:
            self.convert()
            self.output_corpus()
