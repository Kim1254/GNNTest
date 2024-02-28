import os
import sys
import re
from subprocess import run, PIPE
from optparse import OptionParser

command_template = '''read_verilog {0}
hierarchy -auto-top
proc
fsm_detect
fsm_extract
fsm_opt
fsm_recode
fsm_info
fsm_map
opt_expr
opt_merge
opt_muxtree
opt_reduce
opt_merge
opt_dff
opt_expr
opt_mem
opt_mem_priority
opt_mem_feedback
memory_bmux2rom
memory_dff
memory_share
opt_mem_widen
memory_collect
memory_map
opt_expr
opt_merge
opt_muxtree
opt_reduce
opt_merge
opt_dff
opt_expr
techmap
opt_expr
opt_merge
opt_muxtree
opt_reduce
opt_merge
opt_dff
opt_expr
dfflibmap -liberty {1}
abc -liberty {1}
opt_expr
opt_merge
opt_muxtree
opt_reduce
opt_merge
opt_dff
opt_expr
write_verilog {2}\\{3}.v
exit
'''

def getTop(toppath, filepath):
    filename = os.path.basename(filepath)
    with open(os.path.join(toppath, "./topmodule.txt")) as f:
        lines = f.readlines()
        for l in lines:
            l = l.replace(" ", "")
            s = l.split(",")
            if len(s) != 2:
                continue
            if s[0] == filename:
                return s[1]
    return None

if __name__ == '__main__':
    optparser = OptionParser()
    optparser.add_option("-l", "--liberty", dest="liberty",
                         default=None, help="Path of liberty, Default=None")
    optparser.add_option("-o", "--output", dest="output",
                         default="output", help="The name of output directory, Default=output")
    (options, args) = optparser.parse_args()
    
    if len(args) != 1:
        print('Usage: synthesizer.py {OPTIONS} {TARGET_DIR_NAME}')
        sys.exit(0)
    
    current = os.getcwd()
    options.liberty = os.path.join(current, options.liberty)
    options.output = os.path.join(current, options.output)
        
    if not os.path.exists(options.output):
        os.makedirs(options.output)
    
    target = args[0]
    
    ban_keywords = ['test.v', 'tb.v', 'test_', '_test', 'tb_', '_tb', 'testbench']
    
    _flist = os.listdir(target)
    for _f in _flist:
        if os.path.isfile(_f):
            continue
        
        base = os.path.basename(_f)
        print(f'\nSyntheizing {base}...')
        os.chdir(os.path.join(current, target, _f))
        
        syn_list = []
        __flist = os.listdir()
        for __f in __flist:
            if any(ban in os.path.basename(__f).lower() for ban in ban_keywords):
                print(f'Skipped reading testbench verilog: {__f}')
                continue
            if os.path.splitext(__f)[1] != '.v':
                continue
            
            syn_list.append(__f)
        
        cmd_input = command_template.format(" ".join(syn_list), options.liberty, options.output, base)
        
        p = run('yosys', stdout=PIPE, input=cmd_input, encoding='ascii')
        if p.returncode != 0:
            raise IOError(f"Failed syntheize {base} circuit: {p.returncode}")
        print('Done.')
    