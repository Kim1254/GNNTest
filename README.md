# GNNTest

- Convert the synthesized circuit into adjacency matrix for training GNN.

> ### Requirements
- [Pyverilog](https://github.com/PyHDI/Pyverilog)

> ### Usage
- Parse verilog into a adjacency matrix
    ```bash
    parse_verilog.py -t {TOP_MODULE} -s {OUTPUT_PATH} {INPUT_PATH}
    ```
    
    - the output file is consisted of (1) adjacency matrix and (2) cell_class dataframe. The path of the output files are `./output/{OUTPUT_PATH}_matrix.csv` and `./output/{OUTPUT_PATH}_column.csv` for each.
    - Example ([yosys/examples/cmos](https://github.com/YosysHQ/yosys/tree/master/examples/cmos))
        ```bash
        parse_verilog.py -t counter -s counter .\test\counter_synth.v .\test\cmos_cells.v
        ```
        
        - Check the `test` and `output` folder for expected input and output. But note that the list of cells are not ordered so that the result of matrix can be different in every execution.
 
> ### Referenced
- https://pytorch-geometric.readthedocs.io/en/latest/modules/nn.html
- https://chioni.github.io/posts/gnn/
