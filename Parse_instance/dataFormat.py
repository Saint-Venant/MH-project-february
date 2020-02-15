import numpy as np


class DataFormat:
    def __init__(self, fileName, dirName):
        self.fileName = fileName
        self.dirName = dirName

        self.content = ''

    def appendValue(self, valueName, value):
        txt = '{} = {};\n\n'.format(valueName, value)
        self.content += txt

    def appendSet(self, setName, s):
        txt = setName + ' = {'
        for x in s:
            txt += '{}, '.format(x)
        if len(s) > 0:
            txt = txt[:-2] + '};\n\n'
        else:
            txt += '};\n\n'
        self.content += txt

    def appendTupleSet(self, setName, s):
        assert(len(s) > 0)
        txt = setName + ' = {'
        for t in s:
            # t: tuple
            txt += '< '
            for x in t:
                txt += '{}, '.format(x)
            txt = txt[:-2] + '>, '
        txt = txt[:-2] + '};\n\n'
        self.content += txt

    def appendMatrix(self, matrixName, mat):
        assert(len(mat) > 0)
        txt = matrixName + ' = [\n'
        for i in range(mat.shape[0]):
            txt += '    ['
            for j in range(mat.shape[1]):
                txt += str(mat[i,j]) + ', '
            txt = txt[:-2] + '],\n'
        txt = txt[:-2] + '\n];\n\n'
        self.content += txt

    def appendTabSet(self, tabName, tab):
        '''
        tab = [s1, s2, ..., sn], where si = set
        '''
        assert(len(tab) > 0)
        txt = tabName + ' = [\n'
        for s in tab:
            txt += '    {'
            for x in s:
                txt += '{}, '.format(x)
            txt = txt[:-2] + '},\n'
        txt = txt[:-2] + '\n];\n\n'
        self.content += txt

    def exportFile(self):
        file = self.dirName + self.fileName
        with open(file, 'w') as f:
            f.write(self.content)

def buildEdges(NeighCom, upperBound, fixedVertices):
    '''
    Create the edges for input to the solver
    '''
    n = len(NeighCom)
    edges = []
    nbEdges = 0
    M = upperBound

    # edges between fixed vertices
    file = [0]
    explored = np.zeros(n, dtype=np.int)
    explored[0] = 1
    while len(file) > 0:
        i = file[0]
        file = file[1:]
        v = NeighCom[i]
        for j in v:
            if (fixedVertices[j] == 1) and (explored[j] == 0):
                # necessarily i!=j
                if i == 0:
                    edges.append((nbEdges, j, i, M))
                    nbEdges += 1
                    M -= 1
                else:
                    # necessarily j!=0
                    edges += [(nbEdges, i, j, M), (nbEdges+1, j, i, M-1)]
                    nbEdges += 2
                    M -= 2
                explored[j] = 1
                file.append(j)

    # other edges
    for i in range(n):
        if fixedVertices[i] != 0:
            v = NeighCom[i]
            for j in v:
                if (i > 0) and (j != i) and (fixedVertices[j] != 0) and \
                   (fixedVertices[i] + fixedVertices[j] < 2):
                    edges.append((nbEdges, i, j, M))
                    nbEdges += 1

    return edges

def writeData(instanceName, NeighCapt, NeighCom, upperBound, \
              dataDir='./', modelType='full'):
    '''
    Write data into the corresponding directory
    '''
    assert(modelType in ['full', 'cover'])
    
    # build a file instance
    fileName = 'OPL_{}.dat'.format(instanceName)
    File = DataFormat(fileName, dataDir)

    # build sets
    n = len(NeighCapt)
    vertices = list(range(n))
    targets = vertices[1:]

    # fixed vertices
    # -> add fixedVertices to the arguments
    #fixedTo0 = list(np.where(fixedVertices == 0)[0])
    #fixedTo1 = list(np.where(fixedVertices == 1)[0])
    fixedVertices = -1*np.ones(n, dtype=np.int)
    fixedVertices[0] = 1

    # build edges (in Com graph)
    edges = buildEdges(NeighCom, upperBound, fixedVertices)

    # create the .dat file
    File.appendSet('vertices', vertices)
    File.appendSet('targets', targets)
    #File.appendSet('fixedTo0', fixedTo0)
    #File.appendSet('fixedTo1', fixedTo1)
    if modelType == 'full':
        File.appendTupleSet('edges', edges)
    File.appendTabSet('NeighCapt', NeighCapt)

    File.exportFile()

    return dataDir + fileName


if __name__ == '__main__':
    import parserInstance
    
    Rcapt = 1
    Rcom = 2
    #instanceName = 'captGRID100_10_10'
    #instanceName = 'captANOR225_9_20'
    instanceName = 'captANOR1500_15_100'
    instanceDir = '../Instances/{}.dat'.format(instanceName)

    # model
    modelType = 'full'

    # parse data
    Acapt, Acom, NeighCapt, NeighCom = parserInstance.parseData(
        instanceDir, Rcapt, Rcom)
    nNodes = Acapt.shape[0]

    # upper bound
    M = 100

    # build a file instance
    output = writeData(instanceName, NeighCapt, NeighCom, M, \
                       modelType=modelType)
