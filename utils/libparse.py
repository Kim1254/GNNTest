from liberty.parser import parse_liberty

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
