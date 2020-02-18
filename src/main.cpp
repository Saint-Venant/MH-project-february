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
  int index;
  int i;
  int j;
  int M;
};

// --- Data of the model
std::vector<int> vertices;
std::vector<int> targets;
std::vector<Edge> edges;

int nbIters = 1000;
int timeLimit = 180;
float eps = 0.00001;

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
  cout << "Display vertices" << endl;
  for (int i=0; i<vertices.size()-1; i++) {
    cout << vertices[i] << " ";
  }
  cout << vertices[vertices.size()-1] << endl << endl;

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
  cout << "Display targets" << endl;
  for (int i=0; i<targets.size()-1; i++) {
    cout << targets[i] << " ";
  }
  cout << targets[targets.size()-1] << endl << endl;

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
}
/*
template <typename T>
void setModel(IloEnv& env, IloModel& model, T& y) {
  // objective function
  IloExpr exprObj(env);
  for (int i=0; i<m; i++) {
    exprObj += y[i];
  }
  IloObjective obj(env, exprObj, IloObjective::Minimize);
  model.add(obj);
  exprObj.end();
}

template <typename T>
void getSolution(IloNum& valueSolution, IloNumArray& ySolution, T& y, IloCplex& cplex) {
  valueSolution = cplex.getObjValue();
  cplex.getValues(ySolution, y);
}

void displaySolution(IloNum& valueSolution, IloNumArray& ySolution) {
  cout << endl << " ----- Master problem ----- " << endl << endl;
  cout << "objective Master: " << valueSolution << endl;
  cout << endl << "Variables y_i" << endl;
  for (int i=0; i<m; i++) {
    cout << "  * y_" << i << " -> " << ySolution[i] << endl;
  }
  cout << endl;
}

void setModelBenders(IloEnv& env1, IloModel& model1, IloNumVarArray& v, IloNumVarArray& u, IloNumArray& ySolution) {
  // objective function
  IloExpr exprObj(env1);
  for (int j=0; j<m; j++) {
    exprObj += -bnd*ySolution[j]*v[j];
  }
  for (int i=0; i<n; i++) {
    exprObj += demand[i]*u[i];
  }
  IloObjective obj(env1, exprObj, IloObjective::Maximize);
  model1.add(obj);
  exprObj.end();

  // constraints
  model1.add(u[0] == 0);
  int s1;
  int s2;
  for (int j=0; j<m; j++) {
    s1 = edges[0][j];
    s2 = edges[1][j];
    model1.add(-v[j] - u[s1] + u[s2] <= 0);
    model1.add(-v[j] + u[s1] - u[s2] <= 0);
  }

  IloExpr exprCtsum(env1);
  for (int i=0; i<n; i++) {
    exprCtsum += u[i];
  }
  for (int j=0; j<m; j++) {
    exprCtsum += v[j];
  }
  model1.add(exprCtsum == 1);
  exprCtsum.end();
}

void getSolutionBenders(IloNum& bendersSolution, IloNumArray& vSolution, IloNumArray& uSolution,
                        IloNumVarArray& v, IloNumVarArray& u, IloCplex& cplex) {
  bendersSolution = cplex.getObjValue();
  cplex.getValues(vSolution, v);
  cplex.getValues(uSolution, u);
}

void displaySolutionBenders(IloNum& bendersSolution, IloNumArray& vSolution, IloNumArray& uSolution) {
  cout << endl << "bendersSolution = " << bendersSolution << endl;
  for (int j=0; j<m; j++) {
    cout << "vSolution_" << j << " = " << vSolution[j] << endl;
  }
  for (int i=0; i<n; i++) {
    cout << "uSolution_" << i << " = " << uSolution[i] << endl;
  }
}

void solveSPBenders(IloNumArray& ySolution, IloNum& bendersSolution, IloNumArray& vSolution, IloNumArray& uSolution) {
  IloEnv envBenders;
  IloModel modelBenders(envBenders);

  // Variables
  IloNumVarArray v(envBenders, m, 0, INT_MAX);
  IloNumVarArray u(envBenders, n, 0, INT_MAX);

  setModelBenders(envBenders, modelBenders, v, u, ySolution);

  // Resolution
  IloCplex cplexBenders(modelBenders);
  cplexBenders.solve();

  // Results
  getSolutionBenders(bendersSolution, vSolution, uSolution, v, u, cplexBenders);
  //displaySolutionBenders(bendersSolution, vSolution, uSolution);

  envBenders.end();
  //cplexBenders.end();
}

template <typename T>
void addCutSPBenders(IloEnv& env, IloModel& model, T& y, IloNumArray& vSolution, IloNumArray& uSolution) {
  IloExpr exprCtsum(env);
  for (int j=0; j<m; j++) {
    exprCtsum += -bnd*y[j]*vSolution[j];
  }
  for (int i=0; i<n; i++) {
    exprCtsum += demand[i]*uSolution[i];
  }
  model.add(exprCtsum <= 0);
  exprCtsum.end();
}
*/

int main(int argc, char* argv[]){
  string instanceName = "";
  for (int i = 0; i < argc; i++){
      if (string(argv[i]).compare("-instanceName") == 0)
          instanceName = argv[i + 1];
  }
  time_t timeBegin = time(NULL);

  IloEnv env;
  setData(instanceName);
  /*
  IloModel model(env);

  // Variables
  IloNumVarArray y(env, m, 0, INT_MAX);

  setModel(env, model, y);
  int step = 1;
  if (method == 1) {
    model.add(IloConversion(env, y, ILOINT));
    step = 2;
  }

  // Resolution
  // --- master problem
  IloNum valueSolution;
  IloNumArray ySolution(env, m);

  // --- sub-problem Benders
  IloNum bendersSolution;
  IloNumArray vSolution(env, m);
  IloNumArray uSolution(env, n);

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
    getSolution(valueSolution, ySolution, y, cplex);
    //displaySolution(valueSolution, ySolution);

    // Solve sub-problem Benders
    solveSPBenders(ySolution, bendersSolution, vSolution, uSolution);
    if (bendersSolution > eps) {
      // add cut
      addCutSPBenders(env, model, y, vSolution, uSolution);
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
    //cplex.end();

    if (!cutAdded && (method == 2) && (step == 1)) {
      model.add(IloConversion(env, y, ILOINT));
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

  env.end();*/

  return 0;
}
