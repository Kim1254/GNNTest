import os
import sys
from optparse import OptionParser

if __name__ == '__main__':
    optparser = OptionParser()
    optparser.add_option("-v", "--version", action="store_true", dest="showversion",
                         default=False, help="Show the version")
    (options, args) = optparser.parse_args()
    
    filelist = args
