/*********************************************
 * OPL 12.9.0.0 Model
 * Author: Matthieu Roux
 * Creation Date: 14 févr. 2020 at 00:27:42
 *********************************************/

// Data
{int} vertices = ...; // all vertices
{int} targets = ...; // targets = all vertices except sink (sink=0)

{int} NeighCaptLarge[vertices] = ...; // for each vertex i, gives all the vertices at a distance <= Rcapt

// fixed vertices
//{int} fixedTo0 = ...;
//{int} fixedTo1 = ...;

// Variables
dvar boolean select[targets];
dvar float+ f[targets][vertices];

minimize sum(i in targets) select[i];

subject to {
  ctCover: forall(i in targets) sum(j in NeighCaptLarge[i] : j > 0) select[j] >= 1;
}


float value = sum(i in targets) select[i];

execute{
	var output = new IloOplOutputFile("output.dat");
	var stat = cplex.status;
	writeln("status = " + stat);
	writeln("value = " + value);
	writeln("select = " + select);
	output.writeln("status = " + cplex.status + ";\n");
	output.writeln("value = " + value + ";\n");
	output.writeln("select = " + select + ";\n");
	output.close();
}