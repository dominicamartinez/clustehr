import subprocess

# Define Apriori algorithm
# The Apriori algorithm used at here is built upon SPMF (http://www.philippe-fournier-viger.com/spmf/) 
# Please download spmf.jar from its website before you run Apriori algorithm
# Reference of Apriori: https://en.wikipedia.org/wiki/Apriori_algorithm
# Input of Apriori is self._input = "***.txt", which includes each patients' diagnosis codes
# Output of Apriori is self._output = "***.txt"


class Apriori():
    
    def __init__(self):
        self._executable = "spmf.jar"
        self._input = "dignosisCodes.txt"
        self._output = "Apriori_output.txt"

    def run(self, min_supp):
        subprocess.call(["java", "-Xmx2g", "-jar", self._executable, "run", "Apriori", self._input, self._output, str(min_supp)])

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
