import numpy as np


class OutputFile:
    def __init__(self, outputFileName='output.dat', outputDir='./'):
        self.file = outputDir + outputFileName
        
        self.status = -1
        self.value = -1
        self.select = -1
        self.loadData()

    def loadData(self):
        with open(self.file, 'r') as f:
            content = f.readlines()
            self.status = int(content[0].split(' = ')[1][:-2])
            self.value = int(content[2].split(' = ')[1][:-2])

            select = []
            row = 4
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





if __name__ == '__main__':
    output = OutputFile()

    print('status = ', output.status, '\n')
    print('value = ', output.value, '\n')
    print('select = ', output.select, '\n')
    print('nb nodes = ', len(output.select), '\n')
