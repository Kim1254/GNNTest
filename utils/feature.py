import numpy as np
import pandas as pd
    
def GetFeatureMatrix(cell_dict, liberty):
    feature_matrix = {}
    
    subset = set(cell_dict.values()) - set(liberty.keys())
    
    if len(subset) != 0:
        raise IOError(f'The feature map cannot cover all classes in cells: {subset}')
    
    keys = list(liberty.keys())
    mat = np.zeros((len(cell_dict), len(liberty)))
    for idx, (cell, feature) in enumerate(cell_dict.items()):
        fidx = keys.index(feature)
        mat[idx][fidx] = 1
    
    feature_matrix['matrix'] = mat
    
    return feature_matrix
