import os
import sys
from optparse import OptionParser

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
                         default=None, help="Output file of computed adjacency matrix. Enter None not to save, Default=None")
    (options, args) = optparser.parse_args()
        
    filelist = args
    
    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)
    
    out_mat = MatrixFromVerilog(filelist,
                  options.topmodule,
                  options.noreorder,
                  options.nobind,
                  options.include,
                  options.define,
                  'instance',
                  options.savefile)
