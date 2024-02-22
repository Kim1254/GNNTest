import numpy as np

import json

import pyverilog
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
from pyverilog.vparser.ast import Input, Output, Wire
from pyverilog.dataflow.dataflow import DFTerminal, DFPartselect
    
def dprint(text):
    #pass # Debug False
    print(text) # Debug True

def MatrixFromVerilog(filelist, topmodule, noreorder, nobind, include, define, lib_modules):
    result = {}
    
    analyzer = VerilogDataflowAnalyzer(filelist, topmodule,
                                       noreorder=noreorder,
                                       nobind=nobind,
                                       preprocess_include=include,
                                       preprocess_define=define)
    analyzer.generate()
    
    # Cell
    instances = analyzer.getInstances()
    sigs = analyzer.getSignals()
    binds = analyzer.getBinddict()
    
    # Check connections using binds
    bind_list = []
    connection = []
    
    for bind, item in binds.items():
        # Verify the signal is correct
        if len(item) != 1: # 0 or clock (more than 1)
            dprint(f'Invalid bind passed: {bind} -> {item}')
            continue
        
        '''
        check bind: top.vs._093_.c, <class 'pyverilog.utils.scope.ScopeChain'>
        (Bind dest:top.vs._093_.c tree:(Terminal top.vs._018_)) assign top_vs__093__c = top_vs__018_;
        '''
        
        dprint(f'check bind: {bind}')
        if bind not in sigs.keys():
            dprint(f'Invalid bind passed: {bind} does not exist in signal list!')
            continue
        
        signal = sigs[bind]
        
        sig_type = None
        for s in signal:
            if sig_type is None or type(s) is not Wire:
                sig_type = type(s)
            if type(s) is not Wire and sig_type is not type(s): # Multiple input/output definition for one signal
                sig_type = None
                break
        
        if sig_type is None:
            dprint(f'The type of signal in {bind} cannot be classified. Check the verilog.')
            continue
        
        dprint(f'sigtype: {sig_type}')
        item_type = type(item[0].tree)
        if item_type is DFTerminal: # Signal <= Signal
            bind_list.append([bind, item[0].tree.name, sig_type])
        elif item_type is DFPartselect: # Signal <= array[msb:lsb]
            bind_list.append([bind, item[0].tree.var, sig_type])
        else: # Integers
            dprint(f'Ignored unsupported bind type: {type(item[0].tree)}, code: {item[0].tocode()}')
        
        for bi in bind_list:
            connection.append([])
            break
        
    
    n = len(instances)
    
    if n == 0:
        raise ValueError("No Instance Exist. Cannot create the adjacency matrix.")
    
    result['connection'] = connection
    
    if len(connection) == 0:
        dprint('Warning: No connection exist, the adjacency matrix has no value')
    
    # Create matrix of cell(instance) -> describe the connection of cells through signals
    mat = np.zeros((n, n))
    result['matrix'] = mat
    
    for i, item1 in enumerate(_inst_list):
        
        for j, item2 in enumerate(_inst_list):
            
            conn_value = 0
            connection = None
            
            if i == j: # Self connection
                conn_value = 1
            elif item1 in _bind_dict and item2 in _bind_dict:
                for bind1 in _bind_dict[item1]:
                    for key1, val1 in bind1.items():
                        for bind2 in _bind_dict[item2]:
                            for key2, val2 in bind2.items():
                                if key1 == key2:
                                    connection = key1
            
            # Give weight of connection with classes
            if connection is not None:
                if connection[0:5] == 'input':
                    conn_value = 1
                elif connection[0:6] == 'output':
                    conn_value = 1
                else:
                    conn_value = 1
            
            mat[i][j] += conn_value
    
    return result