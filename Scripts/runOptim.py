import sys
sys.path.append('../')

import os
import shutil
import numpy as np
import matplotlib.pyplot as plt

from Parse_instance import parserInstance
from Parse_instance import dataFormat
from Parse_instance import readOutput
from Parse_instance import displaySolution

instanceName = 'captANOR225_9_20'
#instanceName = 'captGRID100_10_10'
#instanceName = 'captANOR900_15_20'
#instanceName = 'captANOR1500_21_500'
instanceDir = '../Instances/'
instancePath = instanceDir + instanceName + '.dat'

oplDir = '../OPL_flow/'
oplModel = 'february_flow_linear'
oplModelPath = oplDir + oplModel + '.mod'

Rcapt = 1
Rcom = 2

# parse data
Acapt, Acom, NeighCapt, NeighCom = parserInstance.parseData(
    instancePath, Rcapt, Rcom)

# upper bound
M = 100

# build a file instance
oplInstanceFile = dataFormat.writeData(instanceName, NeighCapt, NeighCom, M, \
                                       dataDir=oplDir)

# run OPL for optim
os.system('oplrun.exe {} {}'.format(oplModelPath, oplInstanceFile))

# delete file instance
os.remove(oplInstanceFile)

# move output file
shutil.move(oplDir+'output.dat', 'output.dat')

# read output
output = readOutput.OutputFile()
solution = np.array([1] + output.select)
score = output.value
displaySolution.display(instancePath, Rcapt, Rcom, solution, score)
plt.show()
