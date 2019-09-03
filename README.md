# Orange hackathon

The Orange Hackathon was a software development event in which researchers and students expanded the platform system [Orange](orange.biolab.si) with modules which can automatically analyze online therapeutic therapies

The hackathon was a part of the project [What Works When for Whom](https://www.esciencecenter.nl/project/what-works-when-for-whom) in which three partners collaborate: [Tactus](tactus.nl), [Psychology, Health and Technology](www.utwente.nl/en/bms/pht/) of the University of Twente and the [Netherlands eScience Center](esciencecenter.nl).

The contact person for this hackathon is Erik Tjong Kim Sang e.tjongkimsang@esciencecenter.nl


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

## Examples

### Small pipeline

<img src="https://raw.githubusercontent.com/e-mental-health/orange-hackathon/master/images/orange-small.jpg" width="50%">

### Medium pipeline

<img src="https://raw.githubusercontent.com/e-mental-health/orange-hackathon/master/images/orange-medium.jpg" width="100%">
