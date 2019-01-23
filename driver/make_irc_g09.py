#! /usr/bin/python

import sys, os
import operations as op
import singlePoint as sp
from optparse import OptionParser

parser = OptionParser() 
parser.add_option("-f", "--file", dest="filename", help="File with optimized geometries (default: output.dat)", default = "output.dat") #, metavar="FILE")
parser.add_option("-p", "--numproc", dest="proc_num", help="Number of procesors (default 4)", default="4") 
parser.add_option("-m", "--memory", dest="mem_num", help="Memory alloted for the computation (deafault: 2GB)", default="2GB") 
parser.add_option("-d", "--dirrection", dest="dirrection", help="dirrection of the IRC (default: reverse)",default = "reverse") 
parser.add_option("-s", "--stepsize", dest="step", help="size of each step in the IRC (default: 5)", default = "5") 
parser.add_option("-x", "--maxpoints", dest="points", help="Number of points in IRC (default: 50)",default = "50") 
parser.add_option("-c", "--checkfile", dest="check", help="Name of the checkfile (default: IRC.chk)", default = "IRC.chk") 
parser.add_option("-a", "--folder", dest="folder", help="Name of the irc folder (default: irc)", default = "irc") 
parser.add_option("-z", "--otheroption", dest="other", help="Any other option that should be added", default = " ") 
parser.add_option("--force", dest="force", help="How should the force constatn be computed: CalcFC, CalcAll, RCFC (default: CalcFC)", default = "CalcFC") 

(options, args) = parser.parse_args()

outfile = options.filename
proc_num = options.proc_num
mem_num = options.mem_num
checkfile = options.check
dirrection = options.dirrection
points = options.points
step = options.step
irc_folder = options.folder
force = options.force
other = options.other

filelines = op.read_lines(outfile)

theory = sp.get_level_of_theory(filelines)
basis = sp.get_basis(filelines)
charge = sp.get_charge(filelines)
multi = sp.get_multiplicity(filelines)
xyz = sp.get_last_xyz(filelines)

os.chdir("../")
if not os.path.isdir(irc_folder):
  os.makedirs(irc_folder)
os.chdir(irc_folder)
inputfile = "input_"+dirrection.split()[0]+".dat"

f = open(inputfile,"w")
f.write("%Nproc="+proc_num+"\n")
f.write("%Mem="+mem_num+"\n")
f.write("%chk="+checkfile+"\n")
f.write("#P  "+theory+"/"+basis+" scf=(tight) irc=("+force+", "+dirrection+", maxpoints="+points+", stepsize="+step+", VeryTight) Int=ultrafine "+other+"\n\n")
f.write("IRC computation\n\n")
f.write(charge+", "+multi+"\n")
for i in range(0,len(xyz[0])):
  for j in range(0,len(xyz)):
    f.write(xyz[j][i]+ "  ")  
  f.write("\n")
f.write("\n")



