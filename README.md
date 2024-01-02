# GNNTest

- Convert the synthesized circuit into adjacency matrix for training GNN.

---

> ### Usage
- Parse verilog into a adjacency matrix
    ```bash
    parse_verilog.py -t {TOP_MODULE} -s {OUTPUT_PATH} {INPUT_PATH}
    ```
    
    - the output file is consisted of (1) adjacency matrix and (2) cell_class dataframe. The path of the output files are `.\parsing\{OUTPUT_PATH}\matrix.csv` and `.\output\{OUTPUT_PATH}\column.csv` for each.
    - Example ([yosys/examples/cmos](https://github.com/YosysHQ/yosys/tree/master/examples/cmos))
        ```bash
        parse_verilog.py -t counter -l .\example\cmos\cmos_cells.lib .\example\cmos\counter_synth.v
        ```
        
        - Check the `example` and `parsing` folder for the correct I/O of parser.
		- Note that you included liberty when you used in synthesis

---

> ### Requirements
- [Yosys](https://github.com/YosysHQ/yosys/)
    - Synthesize verilog files with Yosys tool.
- [Pyverilog](https://github.com/PyHDI/Pyverilog)
    - You shuold install the [Icarus Verilog](https://bleyer.org/icarus/) matching to the Pyverilog.
- [liberty-parser](https://pypi.org/project/liberty-parser/)
- torch==2.1.0
- torchvision==0.16.0
- torchaudio==2.1.0
- torch_geometric==2.4.0
