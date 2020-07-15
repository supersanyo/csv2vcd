# csv2vcd
Convert csv file to vcd or vec stimulus file for circuit simulation in python3

## Usage
Use the wrapper function in `csv2vcd.py` to generate both `.vcd` and `.vec` files

### Example
#### Sample Wrapper csv2vcd.py
```python
import sys
from CSVTable import *

if len(sys.argv) !=2:
    print("Usage: python3 csv2vcd.py csv_file")
    exit(1)

table = CSVTable(sys.argv[1])

# Generates .vcd file
table.csv2vcd()

# Generates .vcdinfo file for spectre
table.csv2vcdinfo()

# Generates .vec file
table.csv2vec()
```
Execute the command `python3 csv2vcd.py sample/sample.csv` to generates the desired files
