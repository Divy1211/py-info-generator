# Python File Information Generator
This script reads all python files inside a directory (recursively) and generates a JSON data file for each python file. This JSON data file contains detailed information about the different objects declared in the python file like classes, functions, and variables.

# Prerequisites
1. Have python 3.6 or higher installed. If you do not have python, install it from [here](https://www.python.org/downloads/).

# How to use
1. Download the script
2. There are 4 variables `IGNORED_DIRS`, `IGNORED_FILES`, `BASE_DIR`, `OUT_DIR` in the script which need to be modified as required
  - `IGNORED_DIRS`: Names of directories to ignore when generating json data files.
  - `IGNORED_FILES`: Names of files to ignore when generating json data files.
  - `BASE_DIR`: This is the directory to recursively search and read python files.
  - `OUT_DIR`: This is the directory to output the json data files to.
3. Run the script
