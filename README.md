Kudi: An open-source python library for the analysis of properties along reaction paths
=======
![Kudi](https://github.com/stvogt/kudi/blob/master/KudiLogo.png)

### Overview
Kudi is a tool that allows effortless extraction of chemically relevant data along 
a reaction path of a chemical reaction. It is build in python 3 and its straightforward structure makes userfriendly and allows for effortless implementation of new capabilities, and extension to any quantum chemistry package. Currently Kudi can be used in conjunction with Orca4.0 and Gaussian09

### Install Kudi
1. Requirements

To run a kudi script you need numpy, scipy and matplotlib
in your python 3 distribiution. The tutorials are made for jupyter-notebook.

2. As standalone python package

Clone the repostitory using git and
add the "kudi' folder to your PYTHONPATH or copy the folder to an existing PYTHONPATH.

3. Using conda

Coming soon.


### Data pre-processing

The Kudi objects containing all the reaction path data, is initialized with an output file.
This output file contains a series of single point computations, one for each point 
of the reaction path. This file has a special structure and needs to be created using 
a kudi pre-processing script. 

1. From an existing IRC or relaxed scan output file.

Use the **make_sp** script  to create the input_sp.dat file that can be run with the electronic structure package (e.g. Orca or 
Gaussian). To list the different options run (**python make_sp_g09.py -h**). This will create an input file of single point computations for each reaction coordinate structure. This file  contains
the lines: 

"Single Point computation for reaction coordinate: " 

followed by the corresponding reaction coordinate of the single point computation. The resulting output_sp.dat file can
then be used as an input for Kudi. 

2. From an transition state structure

If you only have a optimized transition state structure and have not yet obtained the reaction path, Kudi can help you
generate the IRC or output file, with the **make_irc_g09.py** script. To check the options run **python make_irc_g09.py-h**
in your shell.


### Using Kudi

In the [tutorials folder](https://github.com/stvogt/kudi/tree/master/tutorials) there are several tutorials that ilustrates the capabilities of Kudi. A complete Manual is currently under construction. 
