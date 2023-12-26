import os
import sys
from optparse import OptionParser

from utils.feature import GetFeature, AdjacencyMatToFeatureMat

if __name__ == '__main__':
    optparser = OptionParser()
    optparser.add_option("-v", "--version", action="store_true", dest="showversion",
                         default=False, help="Show the version")
    optparser.add_option("-I", "--include", dest="include", action="append",
                         default=[], help="Feature list that helps matching the cell class, Default=None")
    optparser.add_option("-s", "--save", dest="savefile",
                         default=None, help="Output file of computed feature matrix. It saves the result in the directory named same as the input path, Default=None")
    (options, args) = optparser.parse_args()
    
    if len(args) != 1:
        print('Usage: generate_feature.py {OPTIONS} {TARGET_PATH}')
        sys.exit(0);
    
    filepath = f'./parsing/{args[0]}'
    
    if not os.path.exists(filepath):
        raise IOError('directory does not exists: ' + filepath);
    
    feature_list = GetFeature(f'{filepath}/column.csv', options.include)
    