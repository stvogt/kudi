#! /usr/bin/python

def opt_ts_gga(method, basis, xyz_file, name='gaussian_job',  procs='4', mem="4GB", charge='0', multi='1', method_sp = 'PBE0', basis_sp = 'def2-TZVP'):
    string = '''
%Nprocs = {3}
%Mem = {4}
%Chk = {2}.chk

# {0}/{1} OPT=(CaclFC,TS} scf=tight

Gaussian Job {2}

{5} {6}
{7}

'''.format(method, basis,  name, procs, mem, charge, multi, xyz_file, method_sp, basis_sp)
    return string

def opt_gga(method, basis, xyz_file, name='gaussian_job',  procs='8', mem="4GB" , charge='0', multi='1', method_sp = 'PBE0', basis_sp = 'def2TZVP'):
    string = '''
%Nprocs = {3}
%Mem = {4}
%Chk = {2}.chk

# {0}/{1} OPT scf=tight

Gaussian Job {2}

{5} {6}
{7}

'''.format(method, basis,  name, procs, mem, charge, multi, xyz_file, method_sp, basis_sp)
    return string

def opt_hgga(method, basis, xyz_file, name='gaussian_job',  procs='8', mem="4GB", charge='0', multi='1',  basis_sp = 'def2TZVP'):
    string = '''
%Nprocs = {3}
%Mem = {4}
%Chk = {2}.chk

# {0}/{1} OPT scf=tight

Gaussian Job {2}

{5} {6}
{7}

'''.format(method, basis,  name, procs, mem, charge, multi, xyz_file,  basis_sp)
    return string

def irc(method, basis, xyz_file, name='gaussian_job',  procs='8', mem="4GB", charge='0', multi='1',  maxcycle = '50', stepsize = '3', maxpoints = "100", forcecte = "CalcFC"):
    return '''
%Nprocs = {3}
%Mem = {4}
%Chk = {2}.chk

# {0}/{1} scf=tight irc=(reverse, Maxcycle = {8}, Stepsize = {9} , Maxpoints = {10}, {11})

Gaussian Job {2}

{5} {6}
{7}

--Link1--

%Nprocs = {3}
%Mem = {4}
%Chk = {2}.chk

# {0}/{1} scf=tight irc=(forward, Maxcycle = {8}, Stepsize = {9} , Maxpoints = {10}, {11})

Gaussian Job {2}

{5} {6}
{7}

'''.format(method, basis,  name, procs, mem, charge, multi, xyz_file, maxcycle, stepsize, maxpoints, forcecte)

def sp():
    return '''
%NProcShared={3}
%Mem={4}
%chk={2}
#P {0}/{1} pop=NBORead scf=tight

Single Point computation for reaction coordinate: {5}

0 1
1    0.973640    -0.671980    0.000000
16    -0.692830    -0.671470    0.000000
7    0.000000    0.848970    0.000000
8    1.263950    0.684090    0.000000


$nbo bndidx $end

--Link1--
'''
