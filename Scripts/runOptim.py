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
#instanceName = 'captANOR1500_15_100'
instanceDir = '../Instances/'
instancePath = instanceDir + instanceName + '.dat'

# algo = 'branch_and_bound_OPL' or 'cutting_planes'
algo = 'cutting_planes'

if algo == 'branch_and_bound_OPL':
    optimDir = '../OPL_flow/'
    oplModel = 'february_flow_linear'
    oplModelPath = optimDir + oplModel + '.mod'
elif algo == 'cutting_planes':
    optimDir = '../src/'
    cppModel = 'main'
    cppPath = optimDir + cppModel
modelType = 'full'

Rcapt = 1
Rcom = 2

# parse data
Acapt, Acom, NeighCapt, NeighCom = parserInstance.parseData(
    instancePath, Rcapt, Rcom)

# upper bound
M = 100

# build a file instance
oplInstanceFile = dataFormat.writeData(
    instanceName, NeighCapt, NeighCom, M, \
    modelType=modelType, dataDir=optimDir)

if algo == 'branch_and_bound_OPL':
    # run OPL for optim
    os.system('oplrun.exe {} {}'.format(oplModelPath, oplInstanceFile))
elif algo == 'cutting_planes':
    # run C++ executable
    os.system('{} -instancePath {}'.format(cppPath, oplInstanceFile))

# delete file instance
os.remove(oplInstanceFile)

if algo == 'branch_and_bound_OPL':
    # move output file
    shutil.move(oplDir+'output.dat', 'output.dat')

# read output
output = readOutput.OutputFile(algo)
solution = np.array([1] + output.select)
if output.isOpt():
    if algo == 'branch_and_bound_OPL':
        score = output.bestInteger
        displaySolution.display(instancePath, Rcapt, Rcom, solution, score)
        plt.show()
    elif algo == 'cutting_planes':
        score = output.infBound
        displaySolution.display(instancePath, Rcapt, Rcom, solution, score)
        plt.savefig('solution.png')
else:
    print('No integer solution found in the given time')
