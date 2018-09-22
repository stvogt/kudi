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
            All_orbs.append(float(orbs_line.group(3)))
            if orbs_line.group(2) == "2.0000":
                Occ_orbs.append(float(orbs_line.group(3)))
            if orbs_line.group(2) == "0.0000":
                Virt_orbs.append(float(orbs_line.group(3)))
                if re.search(endstring,lines[lineNum+1]):
                    break
    return (Occ_orbs, Virt_orbs, All_orbs)


def get_symm_orbs(lines,startline=0,  endstring="^\s*$"):
    ''' Extracts the oribtal energy of each irrep '''
    Occ_orbs ={}    
    Virt_orbs = {}  
    All_orbs = {}   
    orbs_re = re.compile(r'^\s+(\d+)\s+(\d\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+-[A-Z].*)')
    count = 0
    for lineNum in range(startline,len(lines)):
        orbs_line = re.search(orbs_re, str(lines[lineNum]))
        if orbs_line:
            count += 1
            symm = orbs_line.group(5).split('-')[0]+orbs_line.group(5).split('-')[1]
            All_orbs[count] = symm
            if orbs_line.group(2) == "2.0000":
                Occ_orbs[count] = symm
            if orbs_line.group(2) == "0.0000":
                Virt_orbs[count] = symm
                if re.search(endstring,lines[lineNum+1]):
                    break
    return (Occ_orbs, Virt_orbs, All_orbs)


def get_xyz(lines, startline=0,  endstring="^\s*$"):
    atom_num =[]
    x_coords = []
    y_coords = []
    z_coords = []
    xyz_re = re.compile('^\s+?([A-Z][a-z]?)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)')
    for lineNum in range(startline,len(lines)):
        #if "CARTESIAN COORDINATES (ANGSTROEM)"
        xyz_line = re.search(xyz_re, str(lines[lineNum]))
        if xyz_line:
            atom_num.append(xyz_line.group(1))
            x_coords.append(xyz_line.group(2))
            y_coords.append(xyz_line.group(3))
            z_coords.append(xyz_line.group(4))
            if lineNum+1 == None:
                break
        if re.search(endstring,lines[lineNum]):
            break
    return (atom_num,x_coords,y_coords,z_coords)

def get_mulliken(lines, startline=0,  endstring="Sum of atomic charges:"):
    atom = []
    atom_num = []
    charge_list = []
    charge_dict = {}
    atom_full_list = []
    for lineNum in range(startline,len(lines)):
        if "MULLIKEN ATOMIC" in lines[lineNum]:
            for lineNum1 in range(lineNum+2,len(lines)):
                if endstring in lines[lineNum1]:
                    break
                number = lines[lineNum1].split()[0]
                atom_num.append(number)
                name =lines[lineNum1].split()[1]
                atom.append(name)
                atom_full = (name+number).replace(':','')
                atom_full_list.append(atom_full)
                if ':' in name:
                    charge = lines[lineNum1].split()[2]
                else:
                    charge = lines[lineNum1].split()[3]
                charge_list.append(charge)
                charge_dict[atom_full] = charge
    return (charge_dict, atom_full_list, charge_list)

def get_npa(lines, startline=0,  endstring="==========="):
    atom = []
    atom_num = []
    charge_list = []
    charge_dict = {}
    atom_full_list = []
    for lineNum in range(startline,len(lines)):
        if "Atom No    Charge" in lines[lineNum]:
            for lineNum1 in range(lineNum+2,len(lines)):
                if re.search(endstring,lines[lineNum1]):
                    break
                number = lines[lineNum1].split()[1]
                atom_num.append(number)
                name =lines[lineNum1].split()[0]
                atom.append(name)
                atom_full = (name+number).replace(':','')
                atom_full_list.append(atom_full)
                charge = lines[lineNum1].split()[2]
                charge_list.append(charge)
                charge_dict[atom_full] = charge
    return (charge_dict, atom_full_list, charge_list)

def get_hirshfeld(lines, startline=0,  endstring="^\s*$"):
    atom = []
    atom_num = []
    charge_list = []
    charge_dict = {}
    atom_full_list = []
    for lineNum in range(startline,len(lines)):
        if "HIRSHFELD ANALYSIS" in lines[lineNum]:
            for lineNum1 in range(lineNum+7,len(lines)):
                if re.search(endstring,lines[lineNum1]):
                    break
                number = lines[lineNum1].split()[0]
                atom_num.append(number)
                name =lines[lineNum1].split()[1]
                atom.append(name)
                atom_full = (name+number).replace(':','')
                atom_full_list.append(atom_full)
                charge = lines[lineNum1].split()[2]
                charge_list.append(charge)
                charge_dict[atom_full] = charge
    return (charge_dict, atom_full_list, charge_list)

def get_lowedin(lines, startline=0, endstring="^\s*$" ):
    atom = []
    atom_num = []
    charge_list = []
    charge_dict = {}
    atom_full_list = []
    for lineNum in range(startline,len(lines)):
        if "LOEWDIN ATOMIC CHARGES" in lines[lineNum]:
            for lineNum1 in range(lineNum+2,len(lines)):
                if re.search(endstring,lines[lineNum1]):
                    break
                number = lines[lineNum1].split()[0]
                atom_num.append(number)
                name =lines[lineNum1].split()[1]
                atom.append(name)
                atom_full = (name+number).replace(':','')
                atom_full_list.append(atom_full)
                if ':' in name:
                    charge = lines[lineNum1].split()[2]
                else:
                    charge = lines[lineNum1].split()[3]
                charge_list.append(charge)
                charge_dict[atom_full] = charge
    return (charge_dict, atom_full_list, charge_list)

