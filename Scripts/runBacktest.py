import sys
sys.path.append('../')

import os
import shutil
import numpy as np
import matplotlib.pyplot as plt

from Parse_instance import parserInstance
from Parse_instance import dataFormat

instanceDir = '../Instances/'
algo = 'cutting_planes'

if algo == 'branch_and_bound_OPL':
    optimDir = '../OPL_flow/'
    oplModel = 'february_flow_linear'
    oplModelPath = oplDir + oplModel + '.mod'
elif algo == 'cutting_planes':
    optimDir = '../src/'
    cppModel = 'main'
    cppPath = optimDir + cppModel
modelType = 'full'

backtestDir = './backtest_cutting_planes12/'
templateSave = backtestDir + 'RESULTS_{}.dat'

Rcapt = 1
Rcom = 2

instances = [x.split('.dat')[0] for x in os.listdir(instanceDir) if '.dat' in x]

for instanceName in instances:
    # parse data
    instancePath = instanceDir + instanceName + '.dat'
    Acapt, Acom, NeighCapt, NeighCom = parserInstance.parseData(
        instancePath, Rcapt, Rcom)

    # upper bound
    M = 1500

    # build a file instance
    oplInstanceFile = dataFormat.writeData(
        instanceName, NeighCapt, NeighCom, M, \
        modelType=modelType, dataDir=optimDir
    )

    if algo == 'branch_and_bound_OPL':
        # run OPL for optim
        os.system('oplrun.exe {} {}'.format(oplModelPath, oplInstanceFile))
    elif algo == 'cutting_planes':
        # run C++ executable
        os.system('{} -instancePath {}'.format(cppPath, oplInstanceFile))

    # delete file instance
    os.remove(oplInstanceFile)

    # move output file
    if algo == 'branch_and_bound_OPL':
        shutil.move(optimDir+'output.dat', templateSave.format(instanceName))
    elif algo == 'cutting_planes':
        shutil.move('output.dat', templateSave.format(instanceName))
