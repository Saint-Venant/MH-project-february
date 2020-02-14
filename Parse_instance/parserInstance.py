import numpy as np


def readInstance(instancePath):
    '''
    instancePath : path to the instance (a .dat file)

    Return a list of n elements:
        n = number of vertices
        each element = [num, x, y] where
            num : id of the vertex (int)
            x, y : coordinates (float)
    '''
    instance = []
    for line in open(instancePath):
        row = line.split()
        tmp = [int(row[0])] + [float(x) for x in row[1:]]
        instance.append(tmp)
    return instance

def distance2(a, b):
    '''
    a, b = [num, x, y] -> elements of the list returned by readInstance

    Return the euclidian distance between points a and b using their (x, y)
    coordinates
    '''
    dist = np.sqrt((a[1] - b[1])**2 + (a[2] - b[2])**2)
    return dist

def make_Adj(instance, R, adjType='Com'):
    '''
    instance : list return by readInstance
    R : int (or float)
    
    Cette fonction fait la matrice d'adjacence telle que Adj[i,j]=1 ssi
    dist(i,j)<=R pour i et j deux sommets

    Pour prendre en compte le fait que le puits ne nécessite pas d'être capté et
    ne peut recevoir aucun capteur, on modélise cela par le fait qu'on forcera
    la solution à contenir le puits tout en s'assurant qu'il ne puisse rien
    capter
    '''
    assert(adjType in ['Capt', 'Com'])
    n = len(instance)
    Adj = np.zeros((n,n), dtype=np.int)
    for i in range(n):
        for j in range(n):
            if distance2(instance[i], instance[j]) <= R:
                Adj[i, j] = 1
    if adjType == 'Capt':
        Adj[0, 1:] = 0
        Adj[1:, 0] = 0
    return Adj

def make_Neigh(Adj):
    '''
    Adj : adjacency matrix (n x n)
    
    Return a list of n elements where:
        n = number of vertices
        each element = [j1, ..., jk] all neighbors in Adj
    '''
    n = Adj.shape[0]
    Neigh = []
    for i in range(n):
        v = list(np.where(Adj[i, :] == 1)[0])
        Neigh.append(v)
    return Neigh

def parseData(instancePath, Rcapt, Rcom):
    '''
    instanceName : path to the instance .dat file
    Rcapt, Rcom : 2 integers

    Do all the pre-computation before running any metaheuristic
    Compute matrices of adjacency and lists of neigbors
    '''
    instance = readInstance(instancePath)
    Acapt = make_Adj(instance, Rcapt, adjType='Capt')
    Acom = make_Adj(instance, Rcom, adjType='Com')
    NeighCapt = make_Neigh(Acapt)
    NeighCom = make_Neigh(Acom)
    return Acapt, Acom, NeighCapt, NeighCom

if __name__ == '__main__':
    instancePath = '../Instances/captANOR225_9_20.dat'
    Rcapt = 1
    Rcom = 2
    Acapt, Acom, NeighCapt, NeighCom = parseData(instancePath, Rcapt, Rcom)
