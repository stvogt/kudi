#! /usr/bin/python

import sys
from kudi import Path
from optparse import OptionParser

parser = OptionParser() 
parser.add_option("-n", "--neutral", dest="neutral", help=" Output of the neutral molecule (default: output.log)", default = "output.log")
parser.add_option("-c", "--cation", dest="cation", help=" Output of the cation molecule (default: output_cat.log)", default = "output_cat.log")
parser.add_option("-a", "--anion", dest="anion", help=" Output of the anion molecule (default: output_an.log)", default = "output_an.log")
parser.add_option("-r", "--relative_energies", dest="rel", help="Options: True or False (default: True)", default = "True")

(options, args) = parser.parse_args()

outN = options.neutral
outC = options.cation
outA = options.anion
rel = options.rel

##Initiate molecule objects
Mol_neut = Path(outN)
Mol_cat  = Path(outC)
Mol_an  = Path(outA)

energyN = Mol_neut.energy(rel)["Energy"]
energyC = Mol_cat.energy(rel)["Energy"]
energyA = Mol_an.energy(rel)["Energy"]

# Function for obtaiing the Ionization Potential and Electron Afinity
def IP(energyC,energyN):
    I = []
    for i in range(0,len(energyN)):
        ip = float(energyC[i])-float(energyN[i])
        I.append(ip)
    return {"Reaction Coordinate": Mol_neut.rxCoord(), "IP":I}

def EA(energyA,energyN):
    A = []
    for i in range(0,len(energyN)):
        ea = float(energyN[i])-float(energyA[i])
        A.append(ea)
    return {"Reaction Coordinate": Mol_neut.rxCoord(), "EA":A}

# Calling the function objects
IP = IP(energyC,energyN)
Mol_neut.save("IP.dat",**IP)
EA = EA(energyA,energyN)
Mol_neut.save("FD.dat",**EA)

# Computing the chemical potential with finite differences
chemPot = Mol_neut.chemPotFinitDiff(IP,EA)

#plot amd save chemical potential profile
Mol_neut.savePlot('chem_pot_FD.svg',r"$\mu(\xi)$", Show=False,**chemPot)
Mol_neut.save("chemPotFD.dat",**chemPot)

###plot and save REF
flux_fd  = Mol_neut.flux(chemPot)
Mol_neut.savePlot('flux_fd.svg',r"J($\xi$)", Show=False, **flux_fd)
Mol_neut.save("fluxFD.dat",**flux_fd)


