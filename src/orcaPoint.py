#! /usr/bin/python


import sys,re,math
import re

def get_property(lines, Tag, position):
  for line in lines:
    if Tag in line:
      property_ = line.split()[position]
      return property_
    
def get_energy(lines):
    return get_property(lines,"FINAL SINGLE POINT ENERGY",4) 

def get_scf(lines):
    return get_property(lines,"Total Energy       :",3) 

def get_orbitals(lines, startline=0,  endstring="^\s*$"):
    orb_num  = []
    Occ_orbs = []
    Virt_orbs = []
    All_orbs = []
    orbs_re = re.compile(r'^\s+(\d+)\s+(\d\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)')
    for lineNum in range(startline,len(lines)):
        orbs_line = re.search(orbs_re, str(lines[lineNum]))
        if orbs_line:
            orb_num.append(orbs_line.group(1))
            All_orbs.append(orbs_line.group(3))
            if orbs_line.group(2) == "2.0000":
                Occ_orbs.append(orbs_line.group(3))
            if orbs_line.group(2) == "0.0000":
                Virt_orbs.append(orbs_line.group(3))
                if re.search(endstring,lines[lineNum+1]):
                    break
    return (Occ_orbs, Virt_orbs, All_orbs)

def get_xyz(lines, startline=0,  endstring="^\s*$"):
    atom_num =[]
    x_coords = []
    y_coords = []
    z_coords = []
    xyz_re = re.compile('^\s+([A-Z][a-z]?)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)')
    for lineNum in range(startline,len(lines)):
        #if "CARTESIAN COORDINATES (ANGSTROEM)"
        xyz_line = re.search(xyz_re, str(lines[lineNum]))
        if xyz_line:
            atom_num.append(xyz_line.group(1))
            x_coords.append(xyz_line.group(2))
            y_coords.append(xyz_line.group(3))
            z_coords.append(xyz_line.group(4))
            if re.search(endstring,lines[lineNum+1]):
                break
    return (atom_num,x_coords,y_coords,z_coords)

