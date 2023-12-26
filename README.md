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
        parse_verilog.py -t counter -s counter .\example\cmos\counter_synth.v .\example\cmos\cmos_cells.v
        ```
        
        - Check the `example` and `parsing` folder for the correct I/O of parser.

---

> ### Requirements
- [Yosys](https://github.com/YosysHQ/yosys)
- [Pyverilog](https://github.com/PyHDI/Pyverilog)
    - You shuold install the Icarus Verilog matching to the Pyverilog.

---

> ### Referenced
- https://pytorch-geometric.readthedocs.io/en/latest/modules/nn.html
- https://chioni.github.io/posts/gnn/
