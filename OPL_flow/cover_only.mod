/*********************************************
 * OPL 12.9.0.0 Model
 * Author: Matthieu Roux
 * Creation Date: 14 févr. 2020 at 19:19:08
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

// Variables
dvar boolean select[targets];

minimize sum(i in targets) select[i];

subject to {
  ctCover: forall(i in targets) sum(j in NeighCapt[i] : j > 0) select[j] >= 1;
}

main {
	thisOplModel.generate();
	cplex.tilim = 30;
	cplex.solve();
	thisOplModel.postProcess();
}

execute{
	var endDate = new Date();
	var solvingTime = endDate.getTime() - startTime;
	
	var gap = cplex.getMIPRelativeGap();
	var bestInteger = cplex.getObjValue();
	var infBound = cplex.getBestObjValue();

	var output = new IloOplOutputFile("output.dat");
	var stat = cplex.status;
	writeln("status = " + stat);
	writeln("gap = " + gap);
	writeln("best integer = " + bestInteger);
	writeln("inf bound = " + infBound);
	writeln("select = " + select);
	writeln("solving time = " + solvingTime);
	output.writeln("status = " + cplex.status + ";\n");
	output.writeln("gap = " + gap + ";\n");
	output.writeln("best integer = " + bestInteger + ";\n");
	output.writeln("inf bound = " + infBound + ";\n");
	output.writeln("select = " + select + ";\n");
	output.writeln("solving time = " + solvingTime + ";\n");
	output.close();
}