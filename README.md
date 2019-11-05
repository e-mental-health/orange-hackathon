# Orange hackathon

[![Maintainability](https://api.codeclimate.com/v1/badges/bba74d89a390004d9ed0/maintainability)](https://codeclimate.com/github/e-mental-health/orange-hackathon/maintainability)

The Orange Hackathon was a software development event in which researchers and students expanded the platform system [Orange](http://orange.biolab.si) with modules which can automatically analyze online therapeutic therapies

The hackathon was a part of the project [What Works When for Whom](https://www.esciencecenter.nl/project/what-works-when-for-whom) in which three partners collaborate: [Tactus](tactus.nl), [Psychology, Health and Technology](www.utwente.nl/en/bms/pht/) of the University of Twente and the [Netherlands eScience Center](esciencecenter.nl).

The contact person for this hackathon is Erik Tjong Kim Sang e.tjongkimsang@esciencecenter.nl


## Installation

In order to use the software developed in the hackathon, you need to have [Orange](http://orange.biolab.si) running at your computer. Next you need to install the hackathon software:

### Orange installation

We install Orange via Anaconda:

1. Download Anaconda from http://www.anaconda.com/distribution (choose the operation system of your computer: Windows, macOS or Linux)
2. When the download is complete: start the Anaconda prompt: under Windows: Anaconda prompt under Anaconda3
3. In the Anaconda3 window, type:
  * conda config --add channels conda-forge (followed by Enter)
  * conda install orange3
  * conda install orange3-text
  * on Windows: mkdir %userprofile%\orange
  * cd %userprofile%\\orange (or cd $HOME/orange on macOS or Linux)
  * git clone https://github.com/e-mental-health/orange-hackathon

**Starting Orange**

1. start the Anaconda prompt: under Windows: Anaconda prompt under Anaconda3
2. In the Anaconda3 window, type:
  * cd %userprofile%\\orange\\orange-hackathon (or cd ~/orange/orange-hackathon)
  * pip install .
  * python -m Orange.canvas

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
