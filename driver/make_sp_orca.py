#! /usr/bin/python

import sys, re, os
from collections import OrderedDict
from optparse import OptionParser
import orcaPoint as orp

parser = OptionParser() 
parser.add_option("-o", "--output_scan", dest="filenameScan", help="File with IRC output (default: output.log) Warning: Use join_irc.py to create the correct outputfile ", default = "output.log") 
parser.add_option("-i", "--input_sp", dest="input_sp", help="File with single points output (default: input_sp.dat)", default = "input_sp.dat")
parser.add_option("-p", "--numproc", dest="proc_num", help="Number of procesors (default: 4)", default="4") 
parser.add_option("-m", "--memory", dest="mem_num", help="Memory alloted for the computation (default: 2GB)", default="2GB") 
parser.add_option("-a", "--folder", dest="folder", help="Name of the Single Point folder (default: sp)", default = "sp") 
parser.add_option("-t", "--theory", dest="theory", help="The level of theory (default: B3LYP)", default = "B3LYP") 
parser.add_option("-b", "--basis", dest="basis", help="The basis set (default: def2-svp))", default = "def2-svp") 
parser.add_option("-n", "--name", dest="name", help="Base name of the job(default: orca))", default = "def2-svp") 
parser.add_option("-c", "--charge", dest="charge", help="charge of the compuation (default: 0)", default = "0") 
parser.add_option("-s", "--multiplicity", dest="multi", help="multiplicity of the computation (default: 1)", default = "1")
parser.add_option("-z", "--otheroption", dest="other", help="Any other option that should be added", default = " ")
#parser.add_option("--pop", dest="population", help="multiply reverse reaction coordinate with -1", default = "NBORead")
parser.add_option("-r", "--auxiliary", dest="aux", help="Which RI method should we use? (RI,RIJK,RIJDX,RIJCOSX) (default=RIJCOSX)", default="RIJCOSX")
parser.add_option("-d", "--dispersion", dest="dispersion", help="Use D3 dispersion correction? (default: True)", default=True)



(options, args) = parser.parse_args()

output_scan = options.filenameScan
input_sp = options.input_sp
proc_num = options.proc_num
mem_num = options.mem_num
sp_folder = options.folder
basis = options.basis
name = options.name
theory = options.theory
multi = options.multi
charge = options.charge
other = options.other
RI = options.aux
#pop = options.population
disp = options.dispersion

def get_rx_coord(lines,startline=0):
    scan_coord = re.compile(r'(-?\d+\.\d+)\sC\s+$')
    for lineNum in range(startline,len(lines)):
       coord_line = re.search(scan_coord,lines[lineNum])
       if coord_line:
           print lines[lineNum]
           return coord_line.group(1)

def xyz_for_sp(lines):
    coordinates = [] # List with all xyz Coordinates
    scan_coords = [] # List with all scaning coordinates
    coords_dict = {} # Dictionary with coords values as key and xyz coords as value
    for lineNum in range(0,len(lines)):
        if "***        THE OPTIMIZATION HAS CONVERGED     ***" in lines[lineNum]:
            xyz = orp.get_xyz(lines,lineNum)
            rx_coord = get_rx_coord(lines,lineNum)
            scan_coords.append(rx_coord)
            coords_dict[rx_coord] = xyz
    return (scan_coords, coords_dict)

lines = open(output_scan,'r').readlines()
Coord_data = xyz_for_sp(lines)
if not os.path.isdir(sp_folder):
  os.makedirs(sp_folder)
os.chdir(sp_folder)

f = open(input_sp,"w")
coords = Coord_data[0]
xyz_all = Coord_data[1]

for coord in coords:
    f.write('# Single point computation of scan coordinate '+coord+'\n\n!'+theory+' '+basis+' '+RI+' '+basis+'/J ')
    xyz = xyz_all[coord]
    if disp == "True":
        f.write(disp+' ')
    f.write(' Grid5 TightSCF \n%base "'+name+'"\n\n%pal\n  nprocs  '+proc_num+"\nend\n\n*xyz "+charge+" "+multi+'\n')
    for i in range(0,len(xyz[0])):
        f.write(xyz[0][i] +'       '+xyz[1][i]+'   '+xyz[2][i] + '  '+xyz[3][i] + '\n')
    f.write('*\n')
    if coord != coords[-1]:
        f.write("\n$new_job\n")

f.close()
os.chdir("../")


