import subprocess

# Define FPMax algorithm
# FPMax Algorithm can return Frequent Maximal Itemsets  
# Reference of FPMax Algorithm: Grahne, G., & Zhu, J. (2003, May). High performance mining of maximal frequent itemsets. 
# Input of FPMax is self._input = "***.txt", which includes each patients' diagnosis codes
# Output of FPMax is self._output = "***.txt"

class FPMax():

    def __init__(self):        
        self._executable = "spmf.jar"
        self._input = "dignosisCodes.txt"
        self._output = "FPMax_output.txt"

    def run(self, min_supp):
        subprocess.call(["java", "-Xmx2g", "-jar", self._executable, "run", "FPMax", self._input, self._output, str(min_supp)])

    def encode_input(self, data):
        pass

    def decode_output(self):
        # read
        lines = []
        try:
            with open(self._output, "rU") as f:
                lines = f.readlines()
        except:
            print ("read_output error")

        # decode
        patterns = []
        for line in lines:
            line = line.strip()
            patterns.append(line.split())

        return patterns
