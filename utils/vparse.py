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
        temp = ScopeChain(value.scopechain[:-1])
        for name, module in instances:
            if temp == name:
                return name
        return None
    
    def find_connection(left, right, is_child=0):
        LEFT, RIGHT = 1, 2
        
        bind_in = left[0]
        
        for item1 in left[1]:
            target1 = item1 if is_child & 1 else item1.tree
            item_type = type(target1)
            if item_type is DFTerminal:
                msb1, lsb1 = item1.msb, item1.lsb
            elif item_type is DFPartselect:
                msb1, lsb1 = target1.msb, target1.lsb
#            elif item_type is DFConcat:
#                print(f'Try left concat: {left}')
#                find_connection((left[0], target1.children()), right, is_child | LEFT)
#                print(f'end: {left}')
#                continue
            else:
                dprint(f'Ignore unsupported left bind type: {type(target1)}, code: {item1.tocode()}')
                continue
            
            conn_in = get_scope(target1)
            if get_sigtype(conn_in) & WIRE:
                dprint(f'Ignore wire output assigning: {conn_in} -> ?\n{item1.tocode()}')
                continue
            conn_in = find_parent(conn_in)
            
            for item2 in right[1]:
                target2 = item2 if is_child & 2 else item2.tree
                item_type = type(target2)
                if item_type in [DFTerminal, DFPartselect]:
                    bind_out = get_scope(target2)
                elif item_type is DFConcat:
#                    print(f'Try right concat: {right}')
#                    find_connection((left[0], (item1)), (right[0], target2.children()), is_child | RIGHT)
#                    print(f'end: {right}')
                    for child in item2.children():
                        bind_out = get_scope(child)
                        if bind_in != bind_out:
                            continue
                        
                        msb2, lsb2 = child.msb, child.lsb
                        
                        conn_out = right[0]
                        if get_sigtype(conn_out) & WIRE:
                            dprint(f'Ignore wire input assigning: {conn_in} -> {conn_out}, {left[0]}. {right[0]}\n{item1.tocode()}{item2.tocode()}')
                            continue
                        conn_out = find_parent(conn_out)
                        
                        # Check msb and lsb are in range if they have
                        if all([x is not None for x in [msb1, lsb1, msb2, lsb2]]):
                            if all([x not in range(lsb2.eval(), msb2.eval() + 1) for x in range(lsb1.eval(), msb1.eval() + 1)]):
                                dprint(f'out of range: {conn_in} -> {conn_out}, {left[0]}. {right[0]}\n{item1.tocode()}{item2.tocode()}')
                                continue
                        
                        # Module <- Signal
                        if len(conn_in.scopechain) != len(conn_out.scopechain):
                            dprint(f'The length of instance does not match: {conn_in} -> {conn_out}, {left[0]}. {right[0]}\n{item1.tocode()}{item2.tocode()}')
                            continue
                        
                        connection.append([conn_in, conn_out])
                        dprint(f'added {conn_in} -> {conn_out}, {left[0]}. {right[0]}\n{item1.tocode()}{item2.tocode()}')
                    continue
                else:
                    dprint(f'Ignore unsupported right bind type: {type(target2)}, code: {item2.tocode()}')
                    continue
                
                if bind_in != bind_out:
                    continue
                
                if item_type is DFTerminal:
                    msb2, lsb2 = item2.msb, item2.lsb
                if item_type is DFPartselect:
                    msb2, lsb2 = target2.msb, target2.lsb
                
                conn_out = right[0]
                if get_sigtype(conn_out) & WIRE:
                    dprint(f'Ignore wire input assigning: {conn_in} -> {conn_out}, {left[0]}. {right[0]}\n{item1.tocode()}{item2.tocode()}')
                    continue
                conn_out = find_parent(conn_out)
                
                # Check msb and lsb are in range if they have
                if all([x is not None for x in [msb1, lsb1, msb2, lsb2]]):
                    if all([x not in range(lsb2.eval(), msb2.eval() + 1) for x in range(lsb1.eval(), msb1.eval() + 1)]):
                        dprint(f'out of range: {conn_in} -> {conn_out}, {left[0]}. {right[0]}\n{item1.tocode()}{item2.tocode()}')
                        continue
                
                # Module <- Signal
                if len(conn_in.scopechain) != len(conn_out.scopechain):
                    dprint(f'The length of instance does not match: {conn_in} -> {conn_out}, {left[0]}. {right[0]}\n{item1.tocode()}{item2.tocode()}')
                    continue
                
                connection.append([conn_in, conn_out])
                dprint(f'added {conn_in} -> {conn_out}, {left[0]}. {right[0]}\n{item1.tocode()}{item2.tocode()}')
    
    # Check connection (bind1 <= bind2)
    for bind1, item1 in binds.items(): # Output bind
        sig = get_sigtype(bind1)
        if sig == 0 or sig & INPUT: # Check bind is output
            continue
        
        for bind2, item2 in binds.items(): # Input bind
            if bind1 == bind2:
                continue
            
            sig = get_sigtype(bind2)
            if sig == 0 or not sig & INPUT: # Check bind is input
                continue
            
            find_connection((bind1, item1), (bind2, item2))
    
    print(f'''Result:
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
        return -1, None
    
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
