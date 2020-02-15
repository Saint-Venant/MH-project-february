import sys
sys.path.append('../')

import os
import shutil
import numpy as np
import matplotlib.pyplot as plt

from Parse_instance import parserInstance
from Parse_instance import dataFormat

instanceDir = '../Instances/'

oplDir = '../OPL_flow/'
oplModel = 'february_flow_linear'
oplModelPath = oplDir + oplModel + '.mod'
modelType = 'full'

backtestDir = './backtest_full_12/'
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
        modelType=modelType, dataDir=oplDir
    )

    # run OPL for optim
    os.system('oplrun.exe {} {}'.format(oplModelPath, oplInstanceFile))

    # delete file instance
    os.remove(oplInstanceFile)

    # move output file
    shutil.move(oplDir+'output.dat', templateSave.format(instanceName))
