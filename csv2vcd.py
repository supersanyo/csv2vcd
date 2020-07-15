"""
#
# csv2vcd - Convert CSV File to VCD for Vector Simulation
#
# CSV Format Example:
#   time, a, b, c, d[3:0], e[2:0], f[7:0]
#    10n, 0, 1, 0,    d10,   b111,    hff 
#  12.5n, 1, 0, 0,     d5,   b010,    ha9 
#
"""

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
