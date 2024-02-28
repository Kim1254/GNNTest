import os
import sys
from optparse import OptionParser

import numpy as np
import pandas as pd

from utils.vparse import ParseVerilog, ParseLiberty, WriteLibVerilog, DumpAsJSON

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
    optparser.add_option("-y", "--y-value", dest="value_y",
                         default=0, help="Value of y, Default=0")
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
    
    result = ParseVerilog(filelist,
                  options.topmodule,
                  options.noreorder,
                  options.nobind,
                  options.include,
                  options.define)
  
    if result is None or len(result) == 0:
        raise IOError('Parsing error: Invalid result')
    
    json_string = DumpAsJSON(result, liberty.keys(), options.value_y)
    
    with open(os.path.join(save_path, f'{options.topmodule}.json'), 'w') as fp:
        fp.write(json_string)
        fp.close()
