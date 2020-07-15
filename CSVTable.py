import csv
import re
from datetime import datetime

class CSVTable:

    symbols = [chr(x) for x in range(33, 127)]  # VCD symbols

    def __init__(self, csv_file, trise=10, tfall=10, vih=1, vil=0):
        self.signals = []
        self.time = []

        self.trise = trise
        self.tfall = tfall
        self.vih = vih
        self.vil = vil

        self._parse(csv_file)
        self.name = (csv_file[:-4] if len(csv_file) > 4 and csv_file[-4:] == '.csv' else csv_file)

    def csv2vcd(self):
        output = open(self.name+'.vcd', 'w')

        """ Print Header """
        output.write("$date %s $end\n" % datetime.now().strftime("%B %d %Y, %H:%M") )
        output.write("$timescale 1ps $end\n")

        assert len(self.signals) <= len(CSVTable.symbols)
        for i in range(len(self.signals)):
            sig = self.signals[i]
            output.write("$var wire %s %s %s $end\n" % (sig.bits, CSVTable.symbols[i], sig.name))
        output.write("$enddefinitions $end\n")

        """ Initial Value Dump """
        output.write("#0\n")
        output.write("$dumpvars\n")
        for i in range(len(self.signals)):
            sig = self.signals[i]
            output.write(CSVTable.vcd_data_str(sig, i, 0))
        output.write("$end\n")

        """ Step through all other values """
        for t in range(1,len(self.time)):
            time = self.time[t]
            output.write("#{}\n".format(time))
            for i in range(len(self.signals)):
                sig = self.signals[i]
                if sig.values[t] != sig.values[t-1]:
                    output.write(CSVTable.vcd_data_str(sig, i, t))
        output.close()

    def csv2vcdinfo(self):
        # Generate vcdinfo file for spectre
        output = open(self.name+'.vcdinfo', 'w')
        output.write(".hier 0\n")
        output.write(".trise {}\n".format(self.trise))
        output.write(".tfall {}\n".format(self.tfall))
        output.write(".vih {}\n".format(self.vih))
        output.write(".vil {}\n".format(self.vil))

        output.write(".in ")
        output.write(' '.join('{}{}'.format( \
            sig.name, \
            "[{}:0]".format(sig.bits-1) if sig.bits>1 else '' ) \
            for sig in self.signals) )
        output.close()

    def csv2vec(self):
        output = open(self.name+'.vec', 'w')
        output.write("radix {}\n".format(' '.join('1'*sig.bits for sig in self.signals)))
        output.write("io {}\n".format(' '.join('i'*sig.bits for sig in self.signals)))
        output.write("vname {}\n".format(' '.join(sig.vec_name() for sig in self.signals)))
        output.write("trise {}\n".format(self.trise))
        output.write("tfall {}\n".format(self.tfall))
        output.write("vih {}\n".format(self.vih))
        output.write("vil {}\n".format(self.vil))
        output.write("tunit 1ps\n")
        
        for i in range(len(self.time)):
            output.write(' '.join( [self.time[i]] + [sig.vec_value(i) for sig in self.signals]) )
            output.write('\n')
            
        output.close()

    def vcd_data_str(sig, i, t):
       return "{0}{2}{1}\n".format( \
            sig.values[t], \
            CSVTable.symbols[i], \
            ' ' if len(sig.values[t]) > 1 else '')
            
    def _parse(self, filename):

        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, skipinitialspace=True, delimiter=',')
            s = next(reader)[1:]

            # Process Header
            for i in range(len(s)):
                sig = Signal(s[i])
                self.signals.append(sig)

            for row in reader:
                self.add_time(row[0])
                for i in range(len(self.signals)):
                    sig = self.signals[i]
                    sig.add_value(row[i+1])
            csvfile.close()

    def print_table(self):
        row = 'time,'
        row += ','.join([sig.name for sig in self.signals])
        print(row)

        i = 0
        while i < len(self.time):
            row = "{},".format(self.time[i])
            row += ','.join([sig.values[i] for sig in self.signals])
            print(row)
            i+=1

    def add_time(self, tstr):
        """
        Parameters
        tstr : str
            The number with unit appended at the end

        return : none
            Add converted time into time list in ps
        """
        unit = tstr[-1]
        if unit == 'p':
            zeros = ''
        elif unit == 'n':
            zeros = '000'
        elif unit == 'u':
            zeros = '000000'
        elif unit == 'm':
            zeros = '000000000'
        else:
            print("Unrecognizable unit of time \"%s\"..." % unit)
            exit(1)
        if tstr.rfind('.') != -1:
            self.time.append( tstr[:-1].replace('.', '')+zeros[len(tstr)-tstr.find('.')-2:] )
        else:
            self.time.append( tstr[:-1]+zeros )

class Signal:
    p = re.compile("(.+)[\<\[]([0-9]+)\:([0-9]+)[\>\]]$")

    def __init__(self, name):
        self.name = name
        self.values = []
        
        s = Signal.p.search(self.name)
        if s:
            res = s.groups()
            self.bits = int(res[1]) +1
            self.name = res[0]
        else:
            self.bits = 1

    def add_value(self, val):
        """
        Parameters
        val : str
            Value to be written as vcd

        return : none
        """
        self.values.append(Signal._conv(val))

    def vec_name(self):
        if self.bits == 1:
            return self.name
        else:
            return "{}<<{}:0>>".format(self.name, self.bits+1)

    def vec_value(self, i):
        # Return value for vec file format
        v = self.values[i]
        return v if v == '1' or v == '0' else "{0:0{1}d}".format(int(v[1:]), self.bits)

    def _conv(s):
        """
        Parameters
        s : str
            Number with prefix of b, d, h representing binary, decimal
            and hex respectively

        return : str
            Return the number in binary with b as prefix
        """
        if s[0] == 'b':
            return s
        elif s[0] == 'd':
            return "b{0:b}".format(int(s[1:]))
        elif s[0] == 'h':
            return "b{0:b}".format(int(s[1:], 16))
        elif s == '1' or s =='0':
            return s
        else:
            print("Incorrect value format")
            return 'b0'