import os
import sys
from optparse import OptionParser

import numpy as np
import pandas as pd

from utils.libparse import ParseLiberty, WriteLibVerilog
from utils.v2m import MatrixFromVerilog
from utils.feature import GetFeatureMatrix

if __name__ == '__main__':
    optparser = OptionParser()
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
    optparser.add_option("-l", "--liberty", dest="liberty",
                         default=[], help="Path of liberty, Default=None")
    optparser.add_option("-s", "--save", dest="savefile",
                         default=None, help="Output directory of computed adjacency matrix. It saves in the directory named same as the topmodule when it is blank, Default=None")
    (options, args) = optparser.parse_args()
    
    filelist = args
    
    if len(filelist) == 0:
        print('Usage: parse_verilog.py {OPTIONS} {VERILOG_PATHS}')
        sys.exit(0)
    
    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)
    
    save = options.savefile
    if save is None:
        save = options.topmodule
    
    save_path = f'.\\parsing\\{save}'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    liberty = {}
    if len(options.liberty) > 0:
        liberty = ParseLiberty(options.liberty)
        
        if len(liberty) == 0:
            raise IOError('Unable to parse liberty: ' + options.liberty)
        
        lib_path = os.path.join(save_path, os.path.basename(options.liberty))
        lib_path = os.path.splitext(lib_path)[0] + '.v'
        WriteLibVerilog(lib_path, liberty)
        filelist.append(lib_path)
    
    result = MatrixFromVerilog(filelist,
                  options.topmodule,
                  options.noreorder,
                  options.nobind,
                  options.include,
                  options.define,
                  liberty.keys())
  
    if result is None or len(result) == 0:
        raise IOError('Empty adjacency matrix, cannot map and save')
    
    # Save matrix
    np.savetxt(f'{save_path}\\matrix.csv', result['matrix'], delimiter=',', fmt='%.2f')
    
    # Save cell info
    df = pd.DataFrame.from_dict(result['cell_class'], orient='index', columns=['class'])
    df.to_csv(f'{save_path}\\cells.csv', sep=',')
    
    feature_matrix = GetFeatureMatrix(result['cell_class'], liberty)
    np.savetxt(f'{save_path}\\feature.csv', feature_matrix['matrix'], delimiter=',', fmt='%.2f')
