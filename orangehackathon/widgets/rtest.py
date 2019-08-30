from Orange.widgets.widget import OWWidget, Output, Input
from Orange.data.table import Table

import pandas
from Orange.data.pandas_compat import table_from_frame

import os

from pathlib import Path
r_path = Path(os.path.dirname(__file__) + '/test.R')

class R(OWWidget):
    name = "R"
    description = "Call R"
    icon = "icons/MarkDuplicates.svg"
    category = "Hackathon"

    class Inputs:
        table = Input("Table", Table)

    class Outputs:
        corpus = Output("Table", Table)

    def __init__(self):
        print('init')

    @Inputs.table
    def callR(self, table):
        import rpy2.robjects as robjects
        if table:
            r_source = robjects.r['source']
            r_source(str(r_path))
            returnvalue = str(robjects.r('testfun("Wouter")'))

            self.Outputs.corpus.send(table_from_frame(pandas.DataFrame.from_dict([{'value': returnvalue}])))

