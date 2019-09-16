# Orange hackathon

The Orange Hackathon was a software development event in which researchers and students expanded the platform system [Orange](http://orange.biolab.si) with modules which can automatically analyze online therapeutic therapies

The hackathon was a part of the project [What Works When for Whom](https://www.esciencecenter.nl/project/what-works-when-for-whom) in which three partners collaborate: [Tactus](tactus.nl), [Psychology, Health and Technology](www.utwente.nl/en/bms/pht/) of the University of Twente and the [Netherlands eScience Center](esciencecenter.nl).

The contact person for this hackathon is Erik Tjong Kim Sang e.tjongkimsang@esciencecenter.nl


## Installation

In order to use the software developed in the hackathon, you need to have [Orange](http://orange.biolab.si) running at your computer. Next you need to install the hacakthon software:

1. Open a command window at your computer (for example xterm or Command Prompt)
2. Dowload the hackathon software by typing: `git clone https://github.com/e-mental-health/orange-hackathon.git`
3. Go to the software directory by typing: `cd orange-hackathon`
4. install the hackathon software: `pip install .`
5. start the Orange software: `python -m Orange.canvas`


## Widgets
**Mail2Tsv**: 
Convert email files to .tsv files, for easy importing as a corpus.

_Instructions:_ select your input folder, and fill in the filter. All files from the subdirectories will be attempted to convert. By default the filter is set to all_documents/ and inbox/, resulting in only the conversion of files inside those subdirectories. 

Once a batch of emails is converted, it will be automatically send them out as a corpus, if any other node is connected. If emails have previously been converted, and the output path/file is still a valid .tsv file, it is enough to press the "Output file > corpus" button. This button only needs to be pressed in a fresh session, if the convert button has been pressed, the output file will automatically be converted.

* this widget requires Tkinter to be installed

**EmailSorter**:
Sorts emails converted by the Mail2Tsv widget in chronological order, based on the "date" column. 

_Instructions:_ No interaction is required, it will start automatically once it receives an input. Clicking on the widget will give the option to sort in ascending, or descending order.

## External data

The WRAD.Wt dictionary used by the module DAAP can be downloaded from

[https://github.com/DAAP/WRAD](https://github.com/DAAP/WRAD)

Note that we also use the [text module](https://github.com/biolab/orange3-text) of Orange3

## Examples

### Small pipeline

<img src="https://raw.githubusercontent.com/e-mental-health/orange-hackathon/master/images/orange-small.jpg" width="60%">

### Medium pipeline

<img src="https://raw.githubusercontent.com/e-mental-health/orange-hackathon/master/images/orange-medium.jpg" width="100%">
