import os
import sys
from optparse import OptionParser

import numpy as np
import pandas as pd

from utils.v2m import MatrixFromVerilog

if __name__ == '__main__':
    optparser = OptionParser()
    optparser.add_option("-v", "--version", action="store_true", dest="showversion",
                         default=False, help="Show the version")
    optparser.add_option("-I", "--include", dest="include", action="append",
                         default=[], help="Include path")
    optparser.add_option("-D", dest="define", action="append",
                         default=[], help="Macro Definition")
    optparser.add_option("-t", "--top", dest="topmodule",
                         default="TOP", help="Top module, Default=TOP")
    optparser.add_option("--nobind", action="store_true", dest="nobind",
                         default=False, help="No binding traversal, Default=False")
    optparser.add_option("--noreorder", action="store_true", dest="noreorder",
                         default=False, help="No reordering of binding dataflow, Default=False")
    optparser.add_option("-s", "--save", dest="savefile",
                         default=None, help="Output directory of computed adjacency matrix. It saves in the directory named same as the topmodule when it is blank, Default=None")
    (options, args) = optparser.parse_args()
    
    filelist = args
    
    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)
    
    result = MatrixFromVerilog(filelist,
                  options.topmodule,
                  options.noreorder,
                  options.nobind,
                  options.include,
                  options.define)
    
    save = options.savefile
    if save is not None:
        save = options.topmodule
    
    path = f'./parsing/{save}'
    if not os.path.exists(path):
        os.makedirs(path)
    
    # Save matrix
    np.savetxt(f'{path}/matrix.csv', result['matrix'], delimiter=',', fmt='%.2f')
    
    # Save cell info
    df = pd.DataFrame.from_dict(result['cell_class'], orient='index', columns=['class'])
    df.to_csv(f'{path}/column.csv', sep=',')
