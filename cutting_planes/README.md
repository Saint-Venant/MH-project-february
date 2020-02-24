#### Small CPLEX C++ API tutorial

**Full example from** : https://github.com/alberto-santini/cplex-example.git

##### Prerequisites

* CPLEX must be installed, of course. Academics can obtain it via the [IBM Academic Initiative](https://developer.ibm.com/academic/).
* You also need a modern version of GCC, that supports at least [C++14](https://en.wikipedia.org/wiki/C++14).

##### Compile and run

* Create a build directory: `mkdir build`.
* Move to the build directory: `cd build`.
* Run cmake: `cmake -DCPLEX_ROOT_DIR=</path/to/ilog> -DCMAKE_BUILD_TYPE=Debug ..`.
  * The path to your CPLEX installation must be such that `</path/to/ilog>/cplex/include/ilcplex/cplex.h` exists.
  * If your compiler is in a non-standard location, you can use `-DCMAKE_CXX_COMPILER=</path/to/compiler>`.
  * Change `Debug` into `Release` if you want to compile in release mode.
  * Here, `</path/to/ilog>` = `/opt/ibm/ILOG/CPLEX_Studio125/`
* Run make: `make`.
* Run the executable: `./cutting_planes`.

##### License

The present work is distributed under the terms of ghe GNU General Public License v3 (see the `LICENSE` file).
