import numpy as np

import pyverilog
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
    
def dprint(text):
    pass # Debug False
    #print(text) # Debug True

def MatrixFromVerilog(filelist, topmodule, noreorder, nobind, include, define):
    result = {}
    
    analyzer = VerilogDataflowAnalyzer(filelist, topmodule,
                                       noreorder=noreorder,
                                       nobind=nobind,
                                       preprocess_include=include,
                                       preprocess_define=define)
    analyzer.generate()
    result['analyzer'] = analyzer
    
    # Cells exclude the topmodule
    instances = analyzer.getInstances()
    
    inst_list = []
    _inst_class = {}
    
    for instance in instances:
        # ScopeChain, str
        module, name = instance
        
        # Skip the topmodule
        if name == topmodule:
            continue
        
        # Verify cell is correct
        if len(module.scopechain) < 2:
            dprint(f'Invalid cell found: {instance}')
            continue
        
        # Verify scopechain is topmodule
        if module.scopechain[0].scopename != topmodule:
            dprint(f'Unmatching TopModule: {instance} with {topmodule}')
            continue
        
        # Append column with ScopeChain.scopename (=The name of cell)
        inst_list.append(module.scopechain[1].scopename)
        
        # Append class of column
        _inst_class[module.scopechain[1].scopename] = name
    
    _inst_list = list(set(inst_list))
    _inst_list.sort()
    
    n = len(_inst_list)
    
    if n == 0:
        raise ValueError("No Instance Exist. Cannot create the adjacency matrix.")
    
    result['cells'] = _inst_list
    result['cell_class'] = _inst_class
    
    sigs = analyzer.getSignals()
    
    sig_list = []
    
    for sig, item in sigs.items():
        # Collect signal in TopModule (except the input and output signals)
        if len(sig.scopechain) != 2:
            continue
        
        # Verify scopechain is topmodule
        if sig.scopechain[0].scopename != topmodule:
            dprint(f'Unmatching TopModule: {sig} with {topmodule}')
            continue
        
        # Append column with ScopeChain.scopename (=The name of signal)
        sig_list.append(sig.scopechain[1].scopename)
            
    _sig_list = list(set(sig_list))
    _sig_list.sort()
    result['singals'] = _sig_list
    
    binds = analyzer.getBinddict()
    
    # {TopModule.Instance.Singal: TopModule.Signal}
    _bind_dict = {}
    
    for bind, item in binds.items():
        # Verify the signal is correct
        if len(item) < 1:
            dprint(f'Invalid bind item found: {bind} -> {item}')
            continue
        
        # Verify scopechain is topmodule
        if bind.scopechain[0].scopename != topmodule:
            dprint(f'Unmatching TopModule: {bind} with {topmodule}')
            continue
        
        # Collect bind of input signals
        if len(bind.scopechain) == 3:
            
            if type(item[0].tree) is not pyverilog.dataflow.dataflow.DFTerminal:
                dprint(f'Unsupported input type entered: {type(item[0].tree)}, {item[0].tree}')
                continue
            
            value = {bind.scopechain[2].scopename: item[0].tree.name.scopechain[1].scopename}
            
            if bind.scopechain[1].scopename in _bind_dict:
                _bind_dict[bind.scopechain[1].scopename].append(value)
            else:
                _bind_dict[bind.scopechain[1].scopename] = [value]
                
        # Collect bind of output signals
        elif len(bind.scopechain) == 2:
            if type(item[0].tree) is not pyverilog.dataflow.dataflow.DFTerminal:
                dprint(f'Unsupported output type entered: {type(item[0].tree)}')
                continue
            
            if len(item[0].tree.name.scopechain) == 2:
                dprint(f'Assigning ignored, {bind}: {item[0].tree.name}')
                continue
            
            value = {item[0].tree.name.scopechain[2].scopename: bind.scopechain[1].scopename}
            
            if bind.scopechain[1].scopename in _bind_dict:
                _bind_dict[item[0].tree.name.scopechain[1].scopename].append(value)
            else:
                _bind_dict[item[0].tree.name.scopechain[1].scopename] = [value]
    
    result['binds'] = _bind_dict
    
    if len(_bind_dict) == 0:
        dprint('Warning: No bind exist, the adjacency matrix has no value')
    
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