/*********************************************
 * OPL 12.9.0.0 Model
 * Author: Matthieu Roux
 * Creation Date: 14 févr. 2020 at 00:27:42
 *********************************************/

float startTime;
execute {
	var startDate = new Date();
	startTime = startDate.getTime();
}

// Data
{int} vertices = ...; // all vertices
{int} targets = ...; // targets = all vertices except sink (sink=0)

{int} NeighCapt[vertices] = ...; // for each vertex i, gives all the vertices at a distance <= Rcapt

// fixed vertices
//{int} fixedTo0 = ...;
//{int} fixedTo1 = ...;

tuple Edge {
  key int id;
  int i;
  int j;
  int M;
};
{Edge} edges = ...;

// Variables
dvar boolean select[targets];
dvar float+ f[edges];

minimize sum(i in targets) select[i];

subject to {
  ctCover: forall(i in targets) sum(j in NeighCapt[i] : j > 0) select[j] >= 1;
  
  ctFlowCirculation1: forall(<e, i, 0, M> in edges) f[<e>] <= M*select[i];
  ctFlowCirculation2: forall(<e, i, j, M> in edges : j > 0) f[<e>] <= M*select[i];
  ctFlowCirculation3: forall(<e, i, j, M> in edges : j > 0) f[<e>] <= M*select[j];
  
  ctFlowConservation: forall(i in targets) sum(<e, i, j, M> in edges) f[<e>] - sum(<e, j, i, M> in edges) f[<e>] == select[i];
}

main {
	thisOplModel.generate();
	cplex.tilim = 30;
	cplex.solve();
	thisOplModel.postProcess();
}

float value = sum(i in targets) select[i];

execute{
	var endDate = new Date();
	var solvingTime = endDate.getTime() - startTime;

	var output = new IloOplOutputFile("output.dat");
	var stat = cplex.status;
	writeln("status = " + stat);
	writeln("value = " + value);
	writeln("select = " + select);
	writeln("solving time = " + solvingTime);
	output.writeln("status = " + cplex.status + ";\n");
	output.writeln("value = " + value + ";\n");
	output.writeln("select = " + select + ";\n");
	output.writeln("solving time = " + solvingTime + ";\n");
	output.close();
}