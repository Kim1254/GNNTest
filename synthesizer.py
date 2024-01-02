import os
import sys
from subprocess import run, PIPE
from optparse import OptionParser

if __name__ == '__main__':
    optparser = OptionParser()
    optparser.add_option("-l", "--liberty", dest="liberty",
                         default=None, help="Path of liberty, Default=None")
    optparser.add_option("-t", "--top", dest="topmodule",
                         default="TOP", help="The name of top module, Default=TOP")
    optparser.add_option("-o", "--output", dest="output",
                         default="output", help="The name of output directory, Default=output")
    (options, args) = optparser.parse_args()
    
    if len(args) != 1:
        print('Usage: synthesizer.py {OPTIONS} {TARGET_DIR_NAME}')
        sys.exit(0)
    
    target = args[0]
    
    flist = []
    _flist = os.listdir(target)
    for f in _flist:
        if 'test' in os.path.basename(f):
            continue
        if os.path.splitext(f)[1] != '.v':
            continue
        
        flist.append(os.path.join(os.path.join(os.getcwd(), target), f))
    
    cmds = f'''read_verilog {" ".join(flist)}
synth
dfflibmap -liberty {options.liberty}
abc -liberty {options.liberty}
opt_clean
write_verilog {options.output}\\{options.topmodule}.v
exit
'''
    
    p = run('yosys', stdout=PIPE, input=cmds, encoding='ascii')
    print(p.returncode)
    print(p.stdout)
    