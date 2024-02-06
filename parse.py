import os

current = os.getcwd()

dataset = os.path.join(current, 'HT_dataset\synth')
file_list = 'topmodule.txt'

parser = os.path.join(current, 'AssembleGNN\parse_verilog.py')

liberty = os.path.join(current, 'vsclib013.lib')

with open(os.path.join(dataset, file_list)) as f:
    for line in f.readlines():
        line = line.replace('\n', '')
        line = line.replace(' ', '')
        args = line.split(',')
        if len(args) != 2:
            continue
            
        print(f'Parsing {args[0]} ...')
        result = os.system(f'{parser} -l {liberty} -s {args[0]} -t {args[1]} {os.path.join(dataset, args[0])}')
        print(f'Result: {result}')
        break
