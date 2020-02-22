import sys
sys.path.append('../')

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas

from Parse_instance.readOutput import OutputFile




class BacktestData:
    def __init__(self, backtestDir):
        self.backtestDir = backtestDir
        self.modelType = -1
        self.algo = -1
        self.Rcapt = -1
        self.Rcom = -1
        self.timeLimit = -1
        self.readInfo()
        assert(self.algo in ['branch_and_bound_OPL', 'cutting_planes'])

        # read outputs
        self.results = [x for x in os.listdir(backtestDir) if '.dat' in x]
        self.outputs = [OutputFile(self.algo, outputFileName=x, \
                                   outputDir=backtestDir) for x in self.results]

    def readInfo(self):
        with open(self.backtestDir + 'info.txt', 'r') as f:
            content = f.readlines()
            self.modelType = content[0].split(' = ')[1][:-1]
            self.algo = content[1].split(' = ')[1][:-1]
            self.Rcapt = int(content[2].split(' = ')[1][:-1])
            self.Rcom = int(content[3].split(' = ')[1][:-1])
            self.timeLimit = int(content[4].split(' = ')[1][:-1])

    def plotPerformance(self, solvingTimes):
        nbSolved = len(solvingTimes)
        time = [0]
        solved = [0]
        for t in solvingTimes:
            time += [t, t]
            solved += [solved[-1], solved[-1]+1]
        time.append(self.timeLimit)
        solved.append(solved[-1])

        plt.figure('Performance diagram')
        plt.plot(time, solved)
        plt.xlabel('time (sec)')
        plt.ylabel('nb solved')
        title = 'Number of instances solved vs. Time\n' + \
                'Model type : {}\nRcapt = {}, Rcom = {}'
        plt.title(title.format(self.modelType, self.Rcapt, self.Rcom))

class BacktestData_OPL(BacktestData):
    def __init__(self, backtestDir):
        super().__init__(backtestDir)

        self.df = pandas.DataFrame(data={
            'instanceName': [x.fileName.split('RESULTS_')[1].split('.dat')[0] \
                             for x in self.outputs],
            'status': [x.status for x in self.outputs],
            'gap': [x.gap for x in self.outputs],
            'bestInteger': [x.bestInteger for x in self.outputs],
            'infBound': [x.infBound for x in self.outputs],
            'solvingTime': [x.solvingTime for x in self.outputs]}
        )

        # sort dataframe by increasing gap
        self.df.sort_values(by='gap', inplace=True)

    def plotPerformance(self):
        # get solving times (transform convert milliseconds to seconds)
        solvingTimes = list(self.df[self.df['status'] == 1]['solvingTime']/1000)
        solvingTimes = np.sort(solvingTimes)
        super().plotPerformance(solvingTimes)

    def plotGap(self):
        plt.subplots(num='Gap')
        plt.plot(self.df['instanceName'], self.df['gap'])
        plt.xticks(rotation=45, horizontalalignment='right', fontsize=6)
        plt.xlabel('Instance')
        plt.ylabel('Gap')
        title = 'Gap for each instance\n' + \
                'Model type : {}\nRcapt = {}, Rcom = {}'
        plt.title(title.format(self.modelType, self.Rcapt, self.Rcom))
        plt.subplots_adjust(bottom=0.25, top=0.85)

class BacktestData_cuttingPlanes(BacktestData):
    def __init__(self, backtestDir):
        super().__init__(backtestDir)

        self.df = pandas.DataFrame(data={
            'instanceName': [x.fileName.split('RESULTS_')[1].split('.dat')[0] \
                             for x in self.outputs],
            'status': [x.status for x in self.outputs],
            'infBound': [x.infBound for x in self.outputs],
            'nbContinuousIt': [x.nbContinuousIt for x in self.outputs],
            'nbIntegerIt': [x.nbIntegerIt for x in self.outputs],
            'solvingTime': [x.solvingTime for x in self.outputs]}
        )

    def plotPerformance(self):
        # get solving times (already in seconds)
        solvingTimes = list(self.df[self.df['status'] == 'optimal']['solvingTime'])
        solvingTimes = np.sort(solvingTimes)
        super().plotPerformance(solvingTimes)


if __name__ == '__main__':
    backtestDir = './backtest_full12/'
    data = BacktestData_OPL(backtestDir)

    
    #backtestDir = './backtest_cutting_planes12/'
    #data = BacktestData_cuttingPlanes(backtestDir)

    data.plotPerformance()
    data.plotGap()

    plt.show()

    
