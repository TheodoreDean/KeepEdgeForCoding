###  Plugin Bindiff ###

> BinDiff is an open-source comparison tool for binary files, that assists vulnerability researchers and engineers to quickly find differences and similarities in disassembled code.


#### precondition

#### software
> IDA pro 7.5

> Ghidra 11.0.3

> bindiff
> It is used to compare the binary and restore the function or constant.

[!https://github.com/google/bindiff] 

####  IDA pro steps
> 1. Open the ELF by IDA 

> 2. Save as the IDA database

> 3. Open another binary(normally BIN) without simbols or tables

> 4. File -> bindiff, get the compare results and recover the known function.

> There are matched functions marked with Green/yellow/green light.

> 5. Select all the matched functions and revover the bin file.

