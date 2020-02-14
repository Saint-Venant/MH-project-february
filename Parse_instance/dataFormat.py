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

# ---- should maybe be removed ! ---
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
        v = NeighCom[i][1]
        for j in v:
            if (fixedVertices[j] == 1) and (explored[j] == 0):
                if i < j:
                    e = (nbEdges, i, j, M)
                else:
                    assert(j < i)
                    e = (nbEdges, j, i, M)
                edges.append(e)
                nbEdges += 1
                explored[j] = 1
                file.append(j)
                M -= 1

    # other edges
    for i in range(n):
        v = NeighCom[i][1]
        for j in v:
            if (i < j) and (fixedVertices[i] + fixedVertices[j] < 2):
                edges.append((nbEdges, i, j, M))
                nbEdges += 1

    return edges

def writeData(instanceName, NeighCapt, NeighCom, upperBound, dataDir='./'):
    '''
    Write data into the corresponding directory
    '''
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

    # build edges (in Com graph)
    #edges = buildEdges(NeighCom, upperBound, fixedVertices)

    # modify NeighCapt to include each vertex in its neighbors
    #NeighCaptLarge = [[i] + NeighCapt[i][1] for i in range(len(NeighCapt))]

    # create the .dat file
    File.appendSet('vertices', vertices)
    File.appendSet('targets', targets)
    #File.appendSet('fixedTo0', fixedTo0)
    #File.appendSet('fixedTo1', fixedTo1)
    #File.appendTupleSet('edges', edges)
    File.appendTabSet('NeighCapt', NeighCapt)

    File.exportFile()

    return dataDir + fileName


if __name__ == '__main__':
    import parserInstance
    
    Rcapt = 1
    Rcom = 2
    instanceName = 'captANOR225_9_20'
    instanceDir = '../Instances/{}.dat'.format(instanceName)

    # parse data
    Acapt, Acom, NeighCapt, NeighCom = parserInstance.parseData(
        instanceDir, Rcapt, Rcom)
    nNodes = Acapt.shape[0]

    # upper bound
    M = 100

    # build a file instance
    output = writeData(instanceName, NeighCapt, NeighCom, M)
