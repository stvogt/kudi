#! /usr/bin/python

import sys, re
import numpy as np
import singlePoint as sp
import gaussianPoint as gsp
import nbo

def process_occ_energies(occ_energies):
  processed_energies = []
  for item in occ_energies:
    if len(item) > 10:
      gaussian_fuckup = item.split("-")
      gaussian_fuckup = filter(None, gaussian_fuckup) 
      for item_stick in gaussian_fuckup:
        processed_energies.append("-"+item_stick)
    else: 
      processed_energies.append(item)
  return processed_energies

def extract_from_blocks(func,blocks):
    list_ = []
    for blockNum in range(0,len(blocks)):
        prop = func(blocks[blockNum])
        list_.append(prop)
    return list_

def get_rxCoord(lines):
  rx_coord = []
  sp_orca_line = re.compile(r'Single point computation of scan coordinate\s+(-?\d+\.\d+)')
  sp_g09_line = re.compile(r'^\s+Single Point computation for reaction coordinate:')
  for Nline in range(0,len(lines)):
    line = lines[Nline]
    match_g09 = re.search(sp_g09_line,line)
    if match_g09: 
       rx_coord.append(line.split()[6])
    match_orca = re.search(sp_orca_line,line)
    if match_orca: 
       rx_coord.append(match_orca.group(1))
  return rx_coord

def get_blocks(lines):
  print "Obtaining the single point blocks...."
  block_lines = []
  blocks = []
  count = 0
  startline = False
  g09_sp_line = re.compile(r'^\s+Single Point computation for reaction coordinate:')
  orca_sp_line = re.compile(r'JOB NUMBER')
  for Nline1 in range(0,len(lines)):
    line1 = lines[Nline1]
    match_g09 = re.search(g09_sp_line,line1)
    if match_g09: 
      startline = True
      count += 1
      for Nline2 in range(Nline1-1,len(lines)):
        line2 = lines[Nline2]
        block_lines.append(line2)
        if "Normal termination of Gaussian 09" in line2:
          break
    match_orca = re.search(orca_sp_line,line1)
    if match_orca: 
      startline = True
      count += 1
      for Nline2 in range(Nline1-1,len(lines)):
        line2 = lines[Nline2]
        block_lines.append(line2)
        if "SCF iterations                  ... " in line2:
          break
    elif startline:
      blocks.append(block_lines)
      block_lines = []
      startline = False
  print "Got it!"
  print "----------------------------------------------------------"
  return blocks

def all_symm_orbs_energ(blocks):
    occ_energ_symm = {}
    virt_energ_symm = {}
    for blockNum in range(0,len(blocks)):
        # Get the dictcionary with the number of orbitals and respective symmetries
        Occ_dict_num = gsp.get_symm_orbs(blocks[blockNum])[0]
        Virt_dict_num = gsp.get_symm_orbs(blocks[blockNum])[1]
        #Get the orbital energies:
        occ_energ = gsp.get_orbitals(blocks[blockNum])[0]
        virt_energ = gsp.get_orbitals(blocks[blockNum])[1]
        all_orbs = gsp.get_orbitals(blocks[blockNum])[2]
        #In the first block initialize the symm_orbital dictcionary
        if blockNum == 0:
            for itemNum in range(1,len(occ_energ)+1):
                symm = Occ_dict_num[itemNum]
                occ_energ_symm[symm] = []
            for itemNum in range(len(occ_energ)+1, len(all_orbs)+1):
                symm = Virt_dict_num[itemNum]
                virt_energ_symm[symm] = []
        # Appending the orbital energies of that point in the IRC with the orbtial enengies 
        for itemNum in range(1,len(occ_energ)+1):
            symm = str(Occ_dict_num[itemNum])
            occ_energ_symm[symm].append(occ_energ[itemNum-1])
        for itemNum in range(len(occ_energ)+1, len(all_orbs)+1):
            #print itemNum
            symm = str(Virt_dict_num[itemNum])
            virt_energ_symm[symm].append(virt_energ[itemNum-len(occ_energ)-1])
    all_energ_symm = dict(occ_energ_symm.items() + virt_energ_symm.items())        
    return(all_energ_symm, occ_energ_symm, virt_energ_symm)

def all_bondOrbitals(blocks):
  orbs = []
  for blockNum in range(0,len(blocks)):
    natorb = nbo.bondOrbitals(blocks[blockNum])
    for key in natorb:
      print key
      print natorb[key]
    break
    orbs.append(charges)
  return orbs


def get_IP(lines_neut,lines_cat):
  cat_enrg = all_energies_non_rel(lines_cat)
  neut_enrg = all_energies_non_rel(lines_neut)
  I = []
  for enrg_item in range(0,len(cat_enrg)):
    ip = float(cat_enrg[enrg_item])-float(neut_enrg[enrg_item])
    I.append(ip)
  return I

def get_EA(lines_neut,lines_an):
  an_enrg = all_energies_non_rel(lines_an)
  neut_enrg = all_energies_non_rel(lines_neut)
  A = []
  for enrg_item in range(0,len(an_enrg)):
    ea = float(neut_enrg[enrg_item])-float(an_enrg[enrg_item])
    A.append(ea)
  return A


# DOES NOT WORK YET FOR ORCA, FIX IT!
def get_all_xyz(blocks,rxc,energy,option):
  xyz_text = ''
  xyz_latex = ''
  xyz_molden = ''
  for blockNum in range(0,len(blocks)):
      #rxc = get_rxCoord(blocks[blockNum])
      header_text = "\nXYZ coordinates for reaction coordinate:  "+rxc[0] +'\n\n'
      header_latex = "\n\\begin{center}\n   XYZ coordinates for reaction coordinate:  "+rxc[0] +'\n\end{center}\n'
      xyz = sp.xyz_pretty_print(blocks[blockNum])
      xyz_text += header_text + xyz[0]
      xyz_latex += header_latex + xyz[1]
      num_atoms = str(len(xyz[2].split('\n'))-1)# Determining how many atoms the molecule has, this is poorly done, I should really write an sp function for that
      header_molden =num_atoms +"\nEnergy="+str(energy[blockNum])+'\n' 
      xyz_molden += header_molden + xyz[2]
  if option == 'text':
        f = open('cartesian.dat','w')
        f.write(xyz_text)
        f.close()
  if option == 'latex':
        f = open('cartesian.tex','w')
        f.write(xyz_latex)
        f.close()
  if option == 'molden':
        f = open('cartesian.mol','w')
        f.write(xyz_molden)
        f.close()

