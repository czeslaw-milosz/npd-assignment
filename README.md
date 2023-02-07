# Final assignment for Data Analysis in Python course at MIM UW, Fall 2022
-------------------------------

# npd-assignment

This is a simple Python package for loading, merging and preprocessing data on CO2 emissions, GDP and population size 
of world countries (data origin: [emission](https://datahub.io/core/co2-fossil-by-nation),
[GDP](https://data.worldbank.org/indicator/NY.GDP.MKTP.CD),
[population](https://data.worldbank.org/indicator/SP.POP.TOTL)). 
The package also calculates basic statistical tables from the data:
- 5 countries with largest CO2 emissions per capita for each year available in the data,
- 5 countries with largest GDP per capita for each year available in the data,
- 5 countries that have largest increase/decrease in CO2 emissions per capita when compared to decade before the most recent year available in data.

## Installation and requirements
In order to install the package and its dependencies, run the following commands:
```shell
cd npd_assignment
pip install .
```
The package was built and tested with `Python 3.11` 
but should be compatible with `Python>=3.9`.



## How to use the package

### Standalone usage:
The package can be used from command line as a standalone Python script. 
The user us required to pass the following arguments:
- ` -e, --emissions_file` - path to a .csv file containing the CO2 emissions data.
- `-g, --gdp_file` - path to a .csv file containing the GDP data.
- `-p, --population_file` - path to a .csv file containing the population data.

Additionally, integer `-start` and `-koniec` arguments can be specified;
if specified, these arguments will be used to restrict the lower and upper range 
of years considered in the analysis. There is also a `-d, --display_mode` argument
that controls results display in the command line. For further information,
see `-h`.

Example of standalone usage:
```shell
cd npd_assignment
python main.py -e path/to/emissions.csv -g path/to/gdp.csv -p path/to/population.csv
```

### Code usage:
The package can obviously be used programatically. `import npd_assignment` 
loads the python library containing all the functionality.

**Please see [`npd_assignment/notebooks/demo.ipynb`](./notebooks/demo.ipynb) for usage example.**


## Profile

Results of profiling with cProfile can be found in this repository:
- `profiling_results.png` - call graph (image),
- `profiling_results.pstats` - full profiling stats (can be conveniently viewed, for example, in `PyCharm`)


## Testing
There is a basic test suite included in the package. A coverage report can be found [here](coverage.txt). Tests can be run within IDE
or using the following command:
```shell
cd npd_assignment/test
pytest .
```
