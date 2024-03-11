import numpy as np
import json

from liberty.parser import parse_liberty

from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
from pyverilog.vparser.ast import Input, Output, Wire
from pyverilog.dataflow.dataflow import DFTerminal, DFPartselect, DFConcat
from pyverilog.utils.scope import ScopeChain


def dprint(text):
    pass
    #print(text)

def ParseVerilog(filelist, topmodule, noreorder, nobind, include, define):
    result = {}
    
    analyzer = VerilogDataflowAnalyzer(filelist, topmodule,
                                       noreorder=noreorder,
                                       nobind=nobind,
                                       preprocess_include=include,
                                       preprocess_define=define)
    analyzer.generate()
    
    # Map parsed data
    instances = analyzer.getInstances()
    sigs = analyzer.getSignals()
    binds = analyzer.getBinddict()
    
    result['cell'] = instances
    #result['signal'] = sigs
    #result['bind'] = binds
    
    # Check connections using binds
    connection = []
    
    INPUT = 1
    OUTPUT = 2
    WIRE = 4
    
    def get_sigtype(bind):
        if bind not in sigs.keys():
            dprint(f'Invalid bind passed: {bind} does not exist in signal list!')
            return 0
        
        signal = sigs[bind]
        sig_type = 0
        for s in signal:
            if type(s) is Input:
                sig_type = sig_type | INPUT
            elif type(s) is Output:
                sig_type = sig_type | OUTPUT
            elif type(s) is Wire:
                sig_type = sig_type | WIRE
        
        if sig_type & INPUT != 0 and sig_type & OUTPUT != 0:
            dprint(f"???: {bind}")
            return 0
        
        return sig_type
    
    def get_scope(item):
        item_type = type(item)
        if item_type is DFTerminal:
            return item.name
        elif item_type is DFPartselect:
            return item.var.name
        
        dprint(f"unknown type: {item.tree}, {item_type}")
        return None
    
    def find_parent(value):
        print(value, type(value))
        temp = ScopeChain(value.scopechain[:-1])
        for name, module in instances:
            if temp == name:
                return name
        return None
    
    # Check connection (bind1 <= bind2)
    for bind1, item1 in binds.items(): # Output bind
        sig1 = get_sigtype(bind1)
        if sig1 == 0 or sig1 & INPUT != 0: # Check bind is output
            continue
        
        for it1 in item1:
            '''
            item_type = type(it1.tree)
            if item_type is DFTerminal or item_type is DFPartselect:
                pass
            elif item_type is DFConcat:
                pass
            else: # Constants
                dprint(f'Ignored unsupported bind1 type: {type(item1[0].tree)}, code: {item1[0].tocode()}')
            '''
            bind_in = None
            if type(it1.tree) in [DFTerminal, DFPartselect, DFConcat]:
                print(it1.tocode())
                bind_in = find_parent(get_scope(it1.tree))
            else:
                dprint(f'Ignored unsupported bind1 type: {type(it1.tree)}, code: {it1.tocode()}')
                continue
            
            for bind2, item2 in binds.items(): # Input bind
                if bind1 == bind2:
                    continue
                
                sig2 = get_sigtype(bind2)
                if sig2 == 0 or sig2 & INPUT == 0: # Check bind is input
                    continue
                
                for it2 in item2:
                    item_type = type(it2.tree)
                    
                    if item_type is DFConcat: # Signal <= {Signal, Signal}
                        for c in it2.tree.children():
                            if bind1 != c.var:
                                continue
                            
                            # Check msb & lsb are in range if items have them
                            if all([x is not None for x in [it1.msb, it1.lsb, c.msb, c.lsb]]):
                                if all([x not in range(c.lsb, c.msb + 1) for x in [it1.msb, it1.lsb]]):
                                    dprint(f"not in range: {bind1} <= {it1.tree}, {it1.msb}, {it1.lsb}, {bind2} <= {c.var}, {c.msb}, {c.lsb}")
                                    continue
                            
                            bind_out = find_parent(c.var)
                            print(f'added {bind_in} -> {bind_out}')
                            connection.append([bind_in, bind_out])
                            break
                        continue
                    elif item_type is DFTerminal: # Signal <= Signal
                        if bind1 != it2.tree.name:
                            continue
                    elif item_type is DFPartselect: # Signal <= Array[msb:lsb]
                        if bind1 != it2.tree.var:
                            continue
                    else: # Others (Signal <= Constants, ...)
                        dprint(f'Ignored unsupported bind2 type: {type(it2.tree)}, code: {it2.tocode()}')
                        continue
                    
                    # Check msb & lsb are in range if items have them
                    if all([x is not None for x in [it1.msb, it1.lsb, it2.msb, it2.lsb]]):
                        if all([x not in range(it2.lsb, it2.msb + 1) for x in [it1.msb, it1.lsb]]):
                            dprint(f"not in range: {bind1} <= {it1.tree}, {it1.msb}, {it1.lsb}, {bind2} <= {it2.tree}, {it2.msb}, {it2.lsb}")
                            continue
                    
                    bind_out = find_parent(bind2)
                    connection.append([bind_in, bind_out])
    
    dprint(f'''Result:
Num of instances: {len(instances)}
Num of signals: {len(sigs)}
Num of binds: {len(binds)}
Num of connections: {len(connection)}
''')
    
    if len(connection) == 0:
        raise ValueError("Error: No connection exists")
    
    result['connection'] = connection
    
    return result

def ParseLiberty(path):
    fp = open(path)
    lib = parse_liberty(fp.read())
    fp.close()
    
    library = {}
    
    cells = lib.get_groups('cell')
    for cell in cells:
        cell_name = cell.args[0]
        
        pins = cell.get_groups('pin')
        
        if pins is None or len(pins) == 0:
            continue
        
        pin_data = {}
        for pin in pins:
            pin_name = pin.args[0]
            direction = pin['direction']
            
            if direction is not None:
                pin_list = [pin_name]
                
                if direction in pin_data.keys():
                    pin_data[direction] = pin_data[direction] + pin_list
                else:
                    pin_data[direction] = pin_list
            
            if direction == 'output':
                function = pin['function']
                if function is not None:
                    pin_data['function'] = function
        
        if len(pin_data) != 0:
            library[cell_name] = pin_data
    
    return library

def WriteLibVerilog(path, library):
    f = open(path, 'w')
    
    f.write(f'// Source: {path}\n')
    
    for cell, pins in library.items():
        inputs = pins.get('input')
        outputs = pins.get('output')
        func = pins.get('function')
        
        if inputs == None or outputs == None:
            continue
        
        f.write(f'\nmodule {cell}({(",".join(inputs+outputs))});\n')
        f.write(f'input {",".join(inputs)};\n')
        f.write(f'output {",".join(outputs)};\n')
        
        if func is not None:
            f.write(f'// function: {func}\n')
        
        f.write('endmodule\n')
    
    f.close()

'''
{
"edge_index":[
	[edge_start],
	[edge_end]
],
### Skipped ### "edge_attr": [
    num_edges * num_edge_features
],
"y": [0 or 1],
"num_nodes": number,
"node_feat": [
    #num_nodes * num_features
]
}
'''

def DumpAsJSON(vdict, lib_keys, value_y):
    instances = sorted(list(vdict['cell']), key=lambda value: value[0].tocode()) # Sort with the name of cell
    connections = vdict['connection']
    sorted_keys = sorted(list(lib_keys))
    
    edge_in = []
    edge_out = []
    node_feature = np.zeros((len(instances), len(sorted_keys)), dtype=np.int8)
    
    def get_instance(key):
        for idx, (name, module) in enumerate(instances):
            if name == key:
                return idx, module
        return -1
    
    for c in connections:
        in_idx, in_feature = get_instance(c[0])
        out_idx, out_feature = get_instance(c[1])
        
        if in_idx == -1 or out_idx == -1:
            continue
        
        if any([x not in sorted_keys for x in [in_feature, out_feature]]):
            continue
        
        edge_in.append(in_idx)
        edge_out.append(out_idx)
        node_feature[in_idx][sorted_keys.index(in_feature)] = 1
        node_feature[out_idx][sorted_keys.index(out_feature)] = 1
    
    output = {'edge_index': [edge_in, edge_out],
        'y': [value_y],
        'num_nodes': len(instances),
        'node_feat': node_feature.tolist()
    }
    
    return json.dumps(output)
