#! /usr/bin/python 

import sys, re, os
import kudi.gaussianPoint as gsp
from optparse import OptionParser

def xyz_for_sp(lines):
    coords_dict = {} # Dictionary with coords values as key and xyz coords as value
    #Boolean definitions
    first = True
    structures = False
    reverse=True
    #Regular expresion definitions
    xyz_re = re.compile('(\s+\d+){3}(\s+-?\d+\.\d+){3}')
    forward_re = re.compile(r'#.*forward')
    inp_re = re.compile("Input orientation")
    zmat_re = re.compile("Z-Matrix orientation")
    #List initiation
    x = []
    y = []
    z = []
    aNum = []
    for lnum in range(0,len(lines)):
        line = lines[lnum]
        match = re.search(xyz_re,line)
        fmatch = re.search(forward_re,line)
        imatch = re.search(inp_re,line)
        zmatch = re.search(zmat_re,line)
        if fmatch:
            reverse = False
        #if "Input orientation:" or "Z-Matrix orientation"in line:
        if imatch or zmatch:
            structures = True
            a = []
            x = []
            y = []
            z = []
            aNum = []
        if match and structures:
            a.append(line.split()[1])
            x.append(line.split()[3])
            y.append(line.split()[4])
            z.append(line.split()[5])
            if "--------------" in lines[lnum+1]:
                if first:
                    coords_dict[0.0000] = [a,x,y,z]
                    first = False
                structures=False
        if "NET REACTION COORDINATE UP TO THIS POINT" in line:
            if reverse:
                rx_coord = -1*float(line.split()[8])
            else:
                rx_coord = float(line.split()[8])
            coords_dict[rx_coord]=[a,x,y,z] 
            last = False

    return coords_dict

parser = OptionParser() 
parser.add_option("-o", "--output_irc", dest="filenameIRC", help="File with IRC output (default: output.log) Warning: Use join_irc.py to create the correct outputfile ", default = "output.log") #, metavar="FILE")
parser.add_option("-i", "--input_sp", dest="input_sp", help="File with single points output (default: input_sp.dat)", default = "input_sp.dat") #, metavar="FILE")
parser.add_option("-p", "--numproc", dest="proc_num", help="Number of procesors (default: 4)", default="4") 
parser.add_option("-m", "--memory", dest="mem_num", help="Memory alloted for the computation (default: 2GB)", default="2GB") 
parser.add_option("-a", "--folder", dest="folder", help="Name of the Single Point folder (default: sp)", default = "sp") 
parser.add_option("-s", "--scf", dest="scf", help="The cut off criterium for scf convergence (default: tight)", default = "tight") 
parser.add_option("-c", "--charge", dest="charge", help="charge of the compuation (default: 0)", default = "0") 
parser.add_option("-n", "--multiplicity", dest="multi", help="multiplicity of the computation (default: 1)", default = "1") 
parser.add_option("-z", "--otheroption", dest="other", help="Any other option that should be added", default = " ") 
parser.add_option("-v", "--invert", dest="bol", help="Make for to rev and viceversa", default = False) 
parser.add_option("--minus1", dest="minus", help="multiply reverse reaction coordinate with -1", default = False) 
parser.add_option("--pop", dest="population", help="Population analysis", default = "NBORead") 
parser.add_option("--pseudo", dest="pseudo", help="Pseudo potential data (default: None)", default = "None") 

(options, args) = parser.parse_args()

input_irc = options.filenameIRC
input_sp = options.input_sp
proc_num = options.proc_num
mem_num = options.mem_num
sp_folder = options.folder
scf = options.scf
multi = options.multi
charge = options.charge
other = options.other
invert = options.bol
minus = options.minus
pop = options.population
pseudo=options.pseudo

filelines = open(input_irc,'r').readlines()

theory = gsp.get_level_of_theory(filelines)
basis = gsp.get_basis(filelines)


if not os.path.isdir(sp_folder):
  os.makedirs(sp_folder)
os.chdir(sp_folder)

f = open(input_sp,'w') 

if not os.path.isdir("CHK"):
  os.makedirs("CHK")

xyz = xyz_for_sp(filelines) 

count = 0
for rxc in sorted(xyz.keys()):
    coords = xyz[rxc]
    f.write("%NProcShared="+proc_num+"\n")
    f.write("%Mem="+mem_num+"\n")
    f.write("%chk=CHK/sp_"+str(count).zfill(3)+".chk\n")
    f.write("#P  "+theory+"/"+basis+" pop="+pop+"  scf="+scf+"\n\n")
    if invert:
      f.write("Single Point computation for reaction coordinate: "+str(-1*rxc)+"\n\n"+str(charge)+" "+str(multi)+"\n")
    else: 
      f.write("Single Point computation for reaction coordinate: "+str(rxc)+"\n\n"+str(charge)+" "+str(multi)+"\n")
    for i in range(0, len(coords[0])):
      f.write(coords[0][i]+"    "+coords[1][i]+"    "+coords[2][i]+"    "+coords[3][i]+"\n")
    f.write("\n")
    if not pseudo=="None":
      p = open("../"+pseudo,"r").read()
      f.write(p)
    if "NBO" in pop:
      f.write("\n$nbo bndidx $end\n")
    if count != len(xyz)-1:
      f.write("\n--Link1--\n")
    else: 
      print("Input file contaiing "+str(count)+" inputs was written to --->  ./sp/"+input_sp)
      f.write("\n\n")
    count += 1
f.close()


