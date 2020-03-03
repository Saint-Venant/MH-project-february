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

    def getSolvingTimes(self):
        # get solving times (convert milliseconds to seconds)
        solvingTimes = list(self.df[self.df['status'] == 1]['solvingTime']/1000)
        solvingTimes = np.sort(solvingTimes)
        return solvingTimes

    def plotGap(self):
        plt.subplots(num='Gap')
        plt.plot(self.df['instanceName'], self.df['gap'], label=self.algo)
        plt.xticks(rotation=45, horizontalalignment='right', fontsize=6)
        plt.xlabel('Instance')
        plt.ylabel('Gap')
        title = 'Gap for each instance\n' + \
                'Model type : {}\nRcapt = {}, Rcom = {}'
        plt.title(title.format(self.modelType, self.Rcapt, self.Rcom))
        plt.legend()
        plt.subplots_adjust(bottom=0.25, top=0.85)

    def getNonOpt(self):
        return self.df[self.df['status'] != 1]

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

    def getSolvingTimes(self):
        # get solving times (already in seconds)
        solvingTimes = list(self.df[self.df['status'] == 'optimal']['solvingTime'])
        solvingTimes = np.sort(solvingTimes)
        return solvingTimes

    def getNonOpt(self):
        return self.df[self.df['status'] != 'optimal']

class Performance:
    def __init__(self):
        pass

    @staticmethod
    def computeAxis(solvingTimes, timeLimit):
        nbSolved = len(solvingTimes)
        time = [0]
        solved = [0]
        for t in solvingTimes:
            time += [t, t]
            solved += [solved[-1], solved[-1]+1]
        time.append(timeLimit)
        solved.append(solved[-1])
        return time, solved

    @staticmethod
    def title(data1, data2):
        assert(data1.modelType == data2.modelType)
        assert(data1.Rcapt == data2.Rcapt)
        assert(data1.Rcom == data2.Rcom)
        title = 'Number of instances solved vs. Time\n' + \
                'Model type : {}\nRcapt = {}, Rcom = {}'
        plt.title(title.format(data1.modelType, data1.Rcapt, data1.Rcom))

    def plotPerformance(self, data1, data2):
        plt.figure('Performance diagram')
        for data in [data1, data2]:
            solvingTimes = data.getSolvingTimes()
            time, solved = self.computeAxis(solvingTimes, data.timeLimit)
            plt.plot(time, solved, label=data.algo)
        plt.xlabel('time (sec)')
        plt.ylabel('nb solved')
        self.title(data1, data2)
        plt.legend()

class LowerBound:
    def __init__(self):
        self.eps = 10**-2

    def computeAxis(self, df1, df2):
        instances = []
        instancesNull = []
        bounds1 = []
        bounds2 = []
        boundsNull = []
        for name in df1['instanceName']:
            if name in list(df2['instanceName']):
                b1 = df1[df1['instanceName'] == name].iloc[0]['infBound']
                b2 = df2[df2['instanceName'] == name].iloc[0]['infBound']
                if b1 > self.eps:
                    instances.append(name)
                    bounds1.append(1)
                    bounds2.append(b2/b1)
                else:
                    instancesNull.append(name)
                    boundsNull.append(b2)
                print(name)
                print(b1, b2)
                print()
        return instances, bounds1, bounds2, instancesNull, boundsNull

    @staticmethod
    def title(data1, data2, num=1):
        assert(data1.modelType == data2.modelType)
        assert(data1.Rcapt == data2.Rcapt)
        assert(data1.Rcom == data2.Rcom)
        if num == 1:
            title = 'Relative lower bound quality\n' + \
                    'Model type : {}\nRcapt = {}, Rcom = {}'
        elif num == 2:
            title = "Lower bounds when 'branch_and_bound_OPL''s is zero\n" + \
                    'Model type : {}\nRcapt = {}, Rcom = {}'
        plt.title(title.format(data1.modelType, data1.Rcapt, data1.Rcom))

    def plot(self, data1, data2):
        '''
        Plot the comparison of lower bounds between data1 (the reference)
        and data2
        > data1 : backtest 'branch_and_bound_OPL'
        > data2 : backtest 'cutting_planes'
        '''
        df1 = data1.getNonOpt()
        df2 = data2.getNonOpt()
        instances, bounds1, bounds2, instancesNull, boundsNull = \
                   self.computeAxis(df1, df2)

        # Plot comparison when data1.lowerBound > 0
        plt.subplots(num='Lower bound quality')
        plt.plot(instances, bounds1, label=data1.algo)
        plt.plot(instances, bounds2, label=data2.algo)
        plt.xticks(rotation=45, horizontalalignment='right', fontsize=6)
        plt.xlabel('Instance')
        plt.ylabel('Relative lower bound')
        self.title(data1, data2, num=1)
        plt.legend()
        plt.subplots_adjust(bottom=0.25, top=0.85)

        # Plot comparison when data1.lowerBound = 0
        fig, ax = plt.subplots(num='Lower bound quality (zero)')
        plt.bar(instancesNull, boundsNull, width=1, label=data2.algo)
        plt.xticks(rotation=45, horizontalalignment='right', fontsize=6)
        ax.set_xlim(-3,4)
        plt.xlabel('Instance')
        plt.ylabel('Lower bound')
        self.title(data1, data2, num=2)
        plt.legend()
        plt.subplots_adjust(bottom=0.25, top=0.85)
        
        


if __name__ == '__main__':
    backtestDir1 = './backtest_full12/'
    data1 = BacktestData_OPL(backtestDir1)
    
    backtestDir2 = './backtest_cutting_planes12/'
    data2 = BacktestData_cuttingPlanes(backtestDir2)

    perf = Performance()
    perf.plotPerformance(data1, data2)

    data1.plotGap()

    low = LowerBound()
    low.plot(data1, data2)

    plt.show()

    
