import numpy as np


class OutputFile:
    def __init__(self, algo, outputFileName='output.dat', outputDir='./'):
        assert(algo in ['branch_and_bound_OPL', 'cutting_planes'])
        
        self.fileName = outputFileName
        self.file = outputDir + outputFileName
        self.algo = algo

        self.status = -1
        self.infBound = -1
        self.select = -1
        self.solvingTime = -1
        if self.algo == 'branch_and_bound_OPL':
            self.gap = -1
            self.bestInteger = -1
            self.loadData_OPL()
        elif self.algo == 'cutting_planes':
            self.nbContinuousIt = -1
            self.nbIntegerIt = -1
            self.sequenceLowBounds = -1
            self.loadData_cuttingPlanes()

    def loadData_OPL(self):
        with open(self.file, 'r') as f:
            content = f.readlines()
        self.status = int(content[0].split(' = ')[1][:-2])
        self.gap = float(content[2].split(' = ')[1][:-2])
        self.bestInteger = int(content[4].split(' = ')[1][:-2])
        self.infBound = float(content[6].split(' = ')[1][:-2])

        select = []
        row = 8
        for elem in content[row].split(' =  ')[1].split(' '):
            if elem[0] == '[':
                select.append(int(elem[1:]))
            elif elem[-1] == '\n':
                select.append(int(elem[:-1]))
            else:
                select.append(int(elem))
        row += 1
        while (len(content[row]) > 1):
            for elem in content[row].split(' '):
                if elem == '':
                    pass
                elif ']' in elem:
                    select.append(int(elem[:-3]))
                elif '\n' in elem:
                    select.append(int(elem[:-1]))
                else:
                    select.append(int(elem))
            row += 1
        self.select = select

        row += 1
        self.solvingTime = int(content[row].split(' = ')[1][:-2])

    def loadData_cuttingPlanes(self):
        with open(self.file, 'r') as f:
            content = f.readlines()
        self.status = content[0].split(' = ')[1][:-2]
        self.infBound = float(content[2].split(' = ')[1][:-2])
        self.nbContinuousIt = int(content[4].split(' = ')[1][:-2])
        self.nbIntegerIt = int(content[6].split(' = ')[1][:-2])
        select = []
        for elem in content[8].split(' = ')[1].split(' '):
            if elem[0] == '[':
                select.append(int(elem[1:]))
            elif ']' in elem:
                select.append(int(elem[:-3]))
            else:
                select.append(int(elem))
        self.select = select
        sequence = []
        for elem in content[10].split(' = ')[1].split(' '):
            if elem[0] == '{':
                sequence.append(float(elem[1:-1]))
            elif '}' in elem:
                sequence.append(float(elem[:-3]))
            else:
                sequence.append(float(elem[:-1]))
        self.sequenceLowBounds = sequence
        self.solvingTime = int(content[12].split(' = ')[1][:-2])

    def displayContent(self):
        print('status = ', self.status, '\n')
        print('inf bound = ', self.infBound, '\n')
        if self.algo == 'branch_and_bound_OPL':
            print('gap = ', self.gap, '\n')
            print('best integer = ', self.bestInteger, '\n')
        elif self.algo == 'cutting_planes':
            print('nb continuous iterations = ', self.nbContinuousIt, '\n')
            print('nb integer iterations = ', self.nbIntegerIt, '\n')
            print('sequence of lower bounds = ', self.sequenceLowBounds, '\n')
        print('nb nodes = ', len(self.select), '\n')
        print('select = ', self.select, '\n')
        print('solving time = ', self.solvingTime)




if __name__ == '__main__':
    #algo = 'cutting_planes'
    algo = 'branch_and_bound_OPL'
    
    output = OutputFile(algo)
    output.displayContent()
    
