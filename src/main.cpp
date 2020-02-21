#include <ilcplex/ilocplex.h>
#include <iostream>
#include <fstream>
ILOSTLBEGIN
using namespace std;

#include <vector>
#include <cmath>
#include <ctime>

struct Edge {
  Edge(int index, int i, int j, int M): index(index), i(i), j(j), M(M) {}
  Edge(): index(-1), i(-1), j(-1), M(-1) {}
  int index;
  int i;
  int j;
  int M;
};

// --- Data of the model
std::vector<int> vertices;
std::vector<int> targets;
std::vector<Edge> edges;
std::vector<std::vector<int>> NeighCapt;
int n;
int nbEdges;
int M = 100;

int nbIters = 1000;
int timeLimit = 180;
float eps = 0.00001;
bool verbose = false;
int method = 2;

Edge readEdge(string entity) {
  int begin;
  int length;
  int index;
  int i;
  int j;
  int M;

  begin = 0;
  length = 1;
  while (entity.compare(begin+length, 1, ",") != 0) {
    length += 1;
  }
  index = std::stoi(entity.substr(begin, length));
  begin = begin + length + 2;
  length = 1;
  while (entity.compare(begin+length, 1, ",") != 0) {
    length += 1;
  }
  i = std::stoi(entity.substr(begin, length));
  begin = begin + length + 2;
  length = 1;
  while (entity.compare(begin+length, 1, ",") != 0) {
    length += 1;
  }
  j = std::stoi(entity.substr(begin, length));
  begin = begin + length + 2;
  length = 1;
  while (entity.compare(begin+length, 1, ">") != 0) {
    length += 1;
  }
  M = std::stoi(entity.substr(begin, length));
  return Edge(index, i, j, M);
}

std::vector<int> readSet(string line) {
  std::vector<int> set;
  int begin = 0;
  int length = 0;
  while (line.compare(begin+length, 1, "{") != 0) {
    length += 1;
  }
  begin = begin + length + 1;
  length = 1;
  while (true) {
    if (line.compare(begin+length, 1, ",") == 0) {
      set.push_back(std::stoi(line.substr(begin, length)));
      begin = begin + length + 2;
    } else if (line.compare(begin+length, 1, "}") == 0) {
      set.push_back(std::stoi(line.substr(begin, length)));
      break;
    } else {
      length += 1;
    }
  }
  return set;
}

void setData(string instanceName) {
  std::ifstream instanceFile;
  std::string line;
  std::stringstream strLine;
  std::string entity;

  instanceFile = std::ifstream(instanceName.c_str());
  if (!instanceFile.is_open()) throw std::runtime_error("No instance file found");

  // read vertices
  std::getline(instanceFile, line);
  strLine = std::stringstream(line);
  std::getline(strLine, entity, '{');
  while (true) {
    std::getline(strLine, entity, ' ');
    if (entity.compare(entity.size()-1, 1, ";") == 0) {
      vertices.push_back(std::stoi(entity.substr(0, entity.size()-2)));
      break;
    } else {
      vertices.push_back(std::stoi(entity.substr(0, entity.size()-1)));
    }
  }
  n = vertices.size();
  if (verbose) {
    cout << "Display vertices" << endl;
    cout << "n = " << n << endl;
    for (unsigned int i=0; i<vertices.size()-1; i++) {
      cout << vertices[i] << " ";
    }
    cout << vertices[vertices.size()-1] << endl << endl;
  }

  // read targets
  std::getline(instanceFile, line);
  std::getline(instanceFile, line);
  strLine = std::stringstream(line);
  std::getline(strLine, entity, '{');
  while (true) {
    std::getline(strLine, entity, ' ');
    if (entity.compare(entity.size()-1, 1, ";") == 0) {
      targets.push_back(std::stoi(entity.substr(0, entity.size()-2)));
      break;
    } else {
      targets.push_back(std::stoi(entity.substr(0, entity.size()-1)));
    }
  }
  if (verbose) {
    cout << "Display targets" << endl;
    for (unsigned int i=0; i<targets.size()-1; i++) {
      cout << targets[i] << " ";
    }
    cout << targets[targets.size()-1] << endl << endl;
  }

  // read edges
  std::getline(instanceFile, line);
  std::getline(instanceFile, line);
  strLine = std::stringstream(line);
  std::getline(strLine, entity, '<');
  while (true) {
    std::getline(strLine, entity, '<');
    if (entity.compare(entity.size()-1, 1, ";") == 0) {
      edges.push_back(readEdge(entity));
      break;
    } else {
      edges.push_back(readEdge(entity));
    }
  }

  nbEdges = edges.size();

  // read NeighCapt
  std::getline(instanceFile, line);
  std::getline(instanceFile, line);
  std::getline(instanceFile, line);
  NeighCapt.push_back(readSet(line));
  while (line.compare(line.size()-1, 1, ",") == 0) {
    std::getline(instanceFile, line);
    NeighCapt.push_back(readSet(line));
  }
  if (verbose) {
    cout << "Display NeighCapt" << endl;
    for (unsigned int i=0; i<NeighCapt.size(); i++) {
      cout << "vertex " << i << " : ";
      for (unsigned int j=0; j<NeighCapt[i].size(); j++) {
        cout << NeighCapt[i][j] << " ";
      }
      cout << endl;
    }
  }
}

template <typename T>
void setModel(IloEnv& env, IloModel& model, T& x) {
  // objective function
  IloExpr exprObj(env);
  for (int i=1; i<n; i++) {
    exprObj += x[i];
  }
  IloObjective obj(env, exprObj, IloObjective::Minimize);
  model.add(obj);
  exprObj.end();

  // cover constraint
  for (int i=1; i<n; i++) {
    IloExpr ctCover(env);
    int k;
    for (unsigned int j=0; j<NeighCapt[i].size(); j++) {
      k = NeighCapt[i][j];
      if (k > 0) {
        ctCover += x[k];
      }
    }
    model.add(ctCover >= 1);
    ctCover.end();
  }
}

template <typename T>
void getSolution(IloNum& valueSolution, IloNumArray& xSolution, T& x, IloCplex& cplex) {
  valueSolution = cplex.getObjValue();
  for (int i=1; i<n; i++) {
    xSolution[i] = cplex.getValue(x[i]);
  }
}

void displaySolution(IloNum& valueSolution, IloNumArray& xSolution) {
  cout << endl << " ----- Master problem ----- " << endl << endl;
  cout << "objective Master: " << valueSolution << endl;
  cout << endl << "Variables x_i" << endl;
  for (int i=1; i<n; i++) {
    cout << "  * x_" << i << " -> " << xSolution[i] << endl;
  }
  cout << endl;
}

void setModelBenders(IloEnv& env1, IloModel& model1, IloNumVarArray& u, IloNumVarArray& v, IloNumVarArray& w,
                     IloNumArray& xSolution) {
  Edge e;

  // objective function
  IloExpr exprObj(env1);
  for (int k=0; k<nbEdges; k++) {
    e = edges[k];
    exprObj += -M*xSolution[e.i]*u[k];
    if (e.j > 0) {
      exprObj += -M*xSolution[e.j]*v[k];
    }
  }
  for (int i=1; i<n; i++) {
    exprObj += xSolution[i]*w[i];
  }
  IloObjective obj(env1, exprObj, IloObjective::Maximize);
  model1.add(obj);
  exprObj.end();

  // constraints
  for (int k=0; k<nbEdges; k++) {
    e = edges[k];
    if (e.j > 0) {
      model1.add(-u[k] - v[k] + w[e.i] - w[e.j] <= 0);
    } else {
      model1.add(-u[k] + w[e.i] <= 0);
    }
  }

  IloExpr exprCtsum(env1);
  for (int k=0; k<nbEdges; k++) {
    e = edges[k];
    exprCtsum += u[k];
    if (e.j > 0) {
      exprCtsum += v[k];
    }
  }
  for (int i=1; i<n; i++) {
    exprCtsum += w[i];
  }
  model1.add(exprCtsum <= 1);
  exprCtsum.end();
}

void getSolutionBenders(IloNum& bendersSolution, IloNumArray& uSolution, IloNumArray& vSolution, IloNumArray& wSolution,
                        IloNumVarArray& u, IloNumVarArray& v, IloNumVarArray& w, IloCplex& cplex) {
  bendersSolution = cplex.getObjValue();
  cplex.getValues(uSolution, u);
  for (int k=0; k<nbEdges; k++) {
    if (edges[k].j > 0) {
      vSolution[k] = cplex.getValue(v[k]);
    }
  }
  for (int i=1; i<n; i++) {
    wSolution[i] = cplex.getValue(w[i]);
  }
}

void displaySolutionBenders(IloNum& bendersSolution, IloNumArray& uSolution, IloNumArray& vSolution, IloNumArray& wSolution) {
  cout << endl << "bendersSolution = " << bendersSolution << endl;
  for (int k=0; k<nbEdges; k++) {
    cout << "uSolution_" << k << " = " << uSolution[k] << endl;
  }
  for (int k=0; k<nbEdges; k++) {
    if (edges[k].j > 0) {
      cout << "vSolution_" << k << " = " << vSolution[k] << endl;
    }
  }
  for (int i=1; i<n; i++) {
    cout << "wSolution_" << i << " = " << wSolution[i] << endl;
  }
}

void solveSPBenders(IloNumArray& xSolution, IloNum& bendersSolution, IloNumArray& uSolution,
                    IloNumArray& vSolution, IloNumArray& wSolution) {
  IloEnv envBenders;
  IloModel modelBenders(envBenders);

  // Variables
  IloNumVarArray u(envBenders, nbEdges, 0, INT_MAX);
  IloNumVarArray v(envBenders, nbEdges, 0, INT_MAX);
  IloNumVarArray w(envBenders, n, 0, INT_MAX);

  setModelBenders(envBenders, modelBenders, u, v, w, xSolution);

  // Resolution
  IloCplex cplexBenders(modelBenders);
  cplexBenders.solve();

  // Results
  getSolutionBenders(bendersSolution, uSolution, vSolution, wSolution, u, v, w, cplexBenders);
  //displaySolutionBenders(bendersSolution, uSolution, vSolution, wSolution);

  envBenders.end();
}

template <typename T>
void addCutSPBenders(IloEnv& env, IloModel& model, T& x, IloNumArray& uSolution, IloNumArray& vSolution, IloNumArray& wSolution) {
  Edge e;
  IloExpr exprCtsum(env);
  for (int k=0; k<nbEdges; k++) {
    e = edges[k];
    exprCtsum += -M*x[e.i]*uSolution[k];
    if (e.j > 0) {
      exprCtsum += -M*x[e.j]*vSolution[k];
    }
  }
  for (int i=1; i<n; i++) {
    exprCtsum += wSolution[i]*x[i];
  }
  model.add(exprCtsum <= 0);
  exprCtsum.end();
}

int main(int argc, char* argv[]){
  string instanceName = "";
  for (int i = 0; i < argc; i++){
      if (string(argv[i]).compare("-instanceName") == 0)
          instanceName = argv[i + 1];
  }
  time_t timeBegin = time(NULL);

  IloEnv env;
  setData(instanceName);

  IloModel model(env);

  // Variables
  IloNumVarArray x(env, n, 0, 1);

  setModel(env, model, x);

  int step = 1;
  if (method == 1) {
    model.add(IloConversion(env, x, ILOINT));
    step = 2;
  }

  // Resolution
  // --- master problem
  IloNum valueSolution;
  IloNumArray xSolution(env, n);

  // --- sub-problem Benders
  IloNum bendersSolution;
  IloNumArray uSolution(env, nbEdges);
  IloNumArray vSolution(env, nbEdges);
  IloNumArray wSolution(env, n);

  bool cutAdded = true;
  int iteration = 0;
  int iterationsStep1 = 0;
  int iterationsStep2 = 0;
  time_t timer = time(NULL);
  double dt = difftime(timer, timeBegin);
  while ((cutAdded) && (iteration < nbIters) && (dt < timeLimit)) {
    cutAdded = false;

    // Master problem
    IloCplex cplex(model);
    cplex.solve();
    getSolution(valueSolution, xSolution, x, cplex);
    //displaySolution(valueSolution, xSolution);
    cout << "VALUE MASTER = " << valueSolution << endl << endl;

    // Solve sub-problem Benders
    solveSPBenders(xSolution, bendersSolution, uSolution, vSolution, wSolution);
    cout << "VALUE BENDERS = " << bendersSolution << endl << endl;
    if (bendersSolution > eps) {
      // add cut
      addCutSPBenders(env, model, x, uSolution, vSolution, wSolution);
      cutAdded = true;
    }

    iteration += 1;
    if (step == 1) {
      iterationsStep1 += 1;
    } else {
      iterationsStep2 += 1;
    }
    timer = time(NULL);
    dt = difftime(timer, timeBegin);

    if (!cutAdded && (method == 2) && (step == 1)) {
      model.add(IloConversion(env, x, ILOINT));
      cutAdded = true;
      step = 2;
    }
  }

  if (cutAdded) {
    cout << endl << endl << "No solution found !" << endl;
    cout << ">> " << iteration << " iterations" << endl;
    cout << ">>   * " << iterationsStep1 << " continuous iterations" << endl;
    cout << ">>   * " << iterationsStep2 << " integer iterations" << endl;
    cout << ">> inf bound : " << valueSolution << endl;
  } else {
    cout << endl << endl << "Optimal solution found !" << endl;
    cout << ">> " << iteration << " iterations" << endl;
    cout << ">>   * " << iterationsStep1 << " continuous iterations" << endl;
    cout << ">>   * " << iterationsStep2 << " integer iterations" << endl;
    cout << ">> objective value : " << valueSolution << endl;
  }

  env.end();

  return 0;
}
