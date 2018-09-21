#!/usr/bin/python

# Authors:  stvogt

import math
import sys
import os
import getpass
import re
import gaussianPoint3 as gsp
from collections import defaultdict

def natCharges (filelines):
  #atomLabel = []
  #atomNumber = []
  charges = {}
  bool = False
  for lineNum in range(0,len(filelines)):
    outline = filelines[lineNum] 
    if "Summary of Natural Population Analysis:" in outline:
      bool = True 
      startline = lineNum + 6
    if "* Total *" in outline:
      endline = lineNum - 1
  if bool:
    for lineNum in range(startline,endline):
      atomlable = filelines[lineNum].split()[0]+filelines[lineNum].split()[1] 
      #atomLabel.append(filelines[lineNum].split()[0]+filelines[lineNum].split()[1])
      charge = filelines[lineNum].split()[2]
      charges[atomlable] = charge
      #charges.append(filelines[lineNum].split()[2])
  return charges

def bondOrder(filelines):
    endstring="^\s*$"
    bndorder = []
    numAtms = len(gsp.get_xyz(filelines)[0])
    for i in range(0,numAtms):
        bndorder.append([])
    atoms = []
    temp = []
    count = 0
    bnd_dicc = {}
    for lineNum in range(0,len(filelines)):
      outline = filelines[lineNum]
      if "Wiberg bond index matrix in the NAO basis:" in outline:
        for lineNum2 in range(lineNum+2,len(filelines)):
          bnd = re.findall('\d+\.\d+', str(filelines[lineNum2]))
          atm = re.search(r"\d+\.\s+(\w+)",str(filelines[lineNum2]))
          if atm:
            count += 1 
            atoms.append(atm.group(1)+str(count))
            if int(filelines[lineNum2].split(".")[0]) == count:
                bndorder[count-1] = bndorder[count-1] + bnd
          if re.search(endstring,filelines[lineNum2]):
              count = 0
          if  "Wiberg bond index, Totals by atom:" in filelines[lineNum2+3]:
            break
    for i in range(0,len(atoms)):
      for j in range(i+1,len(bndorder[0])):
        #print atoms[i+1]+"-"+atoms[j+1]
        bnd_dicc[atoms[i]+"-"+atoms[j]] = bndorder[i][j]
    return bnd_dicc


def bondOrbitals(filelines):
  nat_orbs = dict()
  for lineNum in range(0,len(filelines)):
    outline = filelines[lineNum]
    if "(Occupancy)   Bond orbital/ Coefficients/ Hybrids" in outline:
      for lineNum1 in range(lineNum+1,len(filelines)):  
        bond_info = re.compile('\d+\.\s+\((\d\.\d+)\)\s+(\w+)\s.*(\d+)\)\s*(\w+)\s+(\d+)-?\s?(\w*)\s*(\d*)-?\s*(\w*)\s*(\d*)')
        bond_detail = re.compile("\(\s+(\d+\.\d+)\%\)\s+(\d+\.\d+)\*\s?(\w+)\s+(\d+).*s\(\s*(\d+.\d+).*p\s?(\d+\.\d+)\(\s+(\d+\.\d+)")
        #lone_pair_detail = re.compile('\d+\.\s+\((\d\.\d+)\)\s+(\w+)\s.*\d+\)\s*(\w+)\s+(\d+).*p\s?(\d+\.\d+)')
        lone_pair_detail = re.compile('\d+\.\s+\((\d\.\d+)\)\s+(\w+)\s.*\d+\)\s*(\w+)\s+(\d+).*s\(\s*(\d+.\d+).*p\s?(\d+\.\d+)\(\s+(\d+\.\d+)')
        d_char = re.compile('.*d\s?(\d+\.\d+)\(\s+(\d+\.\d+)')
        new_nbo = re.compile("\d+\.\s+\(\d\.\d+\)")

        match = bond_info.search(str(filelines[lineNum1]))
        lp = lone_pair_detail.search(str(filelines[lineNum1]))
        match_d_lp = d_char.search(str(filelines[lineNum1]))

        if match:
          occup = match.group(1)
          type  = match.group(2)
          number = match.group(3)
          atom1 = match.group(4)
          atomNum1 = match.group(5)
          atom2 = match.group(6)
          atomNum2 = match.group(7)
          atom3 = match.group(8)
          atomNum3 = match.group(9)

          bond = []
          for lineNum2 in range(lineNum1+1,len(filelines)):  
            match1 = bond_detail.search(str(filelines[lineNum2]))
            match_d = d_char.search(str(filelines[lineNum2]))

            if match1 and match_d:
              coef = match1.group(2)
              atom = match1.group(3)
              atmNum = match1.group(4)
              s_per = match1.group(5)
              panteil = match1.group(6)
              p_per = match1.group(7)
              danteil = match_d.group(1)
              d_per = match_d.group(2)
              #print d_per
              bond.append(coef+'sp$^{'+panteil+'}$'+'('+atom+atmNum+')')
              if atomNum3:
                nat_orbs.setdefault(atom1+atomNum1+'-'+atom2+atomNum2+'-'+atom3+atomNum3+'('+number+')',[]).append(atom+atmNum+': '+p_per+'\% p'+' '+s_per+'\% s'+' '+d_per+'\% d') 
              elif atomNum2:
                nat_orbs.setdefault(atom1+atomNum1+'-'+atom2+atomNum2+'('+number+')',[]).append(atom+atmNum+': '+p_per+'\% p'+' '+s_per+'\% s'+' '+d_per+'\% d') 

            elif match1 and not match_d:
              coef = match1.group(2)
              atom = match1.group(3)
              atmNum = match1.group(4)
              s_per = match1.group(5)
              panteil = match1.group(6)
              p_per = match1.group(7)
              bond.append(coef+'sp$^{'+panteil+'}$'+'('+atom+atmNum+')')
              if atomNum3:
                nat_orbs.setdefault(atom1+atomNum1+'-'+atom2+atomNum2+'-'+atom3+atomNum3+'('+number+')',[]).append(atom+atmNum+': '+p_per+'\% p'+' '+s_per+'\% s'+' 0.00\% d') 
              elif atomNum2:
                nat_orbs.setdefault(atom1+atomNum1+'-'+atom2+atomNum2+'('+number+')',[]).append(atom+atmNum+': '+p_per+'\% p'+' '+s_per+'\% s'+' 0.00\% d') 

            if new_nbo.search(str(filelines[lineNum2])):
              if atomNum3:
                # setdefault allows to associate a list to the diccionary keys in this case the type of bond nbo and occupancies
                # are put into a list and the key is the bond eg: Ge1-Ge2
                nat_orbs.setdefault(atom1+atomNum1+'-'+atom2+atomNum2+'-'+atom3+atomNum3+'('+number+')',[]).append(type) 
                nat_orbs.setdefault(atom1+atomNum1+'-'+atom2+atomNum2+'-'+atom3+atomNum3+'('+number+')',[]).append(occup) 
                nat_orbs.setdefault(atom1+atomNum1+'-'+atom2+atomNum2+'-'+atom3+atomNum3+'('+number+')',[]).append('+'.join(bond)) 
              elif atomNum2:
                nat_orbs.setdefault(atom1+atomNum1+'-'+atom2+atomNum2+'('+number+')',[]).append(type) 
                nat_orbs.setdefault(atom1+atomNum1+'-'+atom2+atomNum2+'('+number+')',[]).append(occup) 
                nat_orbs.setdefault(atom1+atomNum1+'-'+atom2+atomNum2+'('+number+')',[]).append('+'.join(bond)) 
              break

        if lp and match_d_lp:
          occup_lp = lp.group(1)
          type_lp = lp.group(2)
          atom_lp = lp.group(3)
          num_lp  = lp.group(4)
          s_perlp = lp.group(5)
          p_pl    = lp.group(6)
          p_perlp = lp.group(7)
          d_pl   = match_d_lp.group(1)
          d_perlp = match_d_lp.group(2)
          if type_lp in 'LP':
            nat_orbs.setdefault(atom_lp+num_lp,[]).append(atom_lp+num_lp+': '+p_perlp+'\% p'+' '+s_perlp+'\% s'+' '+d_perlp+'\% d') 
            nat_orbs.setdefault(atom_lp+num_lp,[]).append(type_lp) 
            nat_orbs.setdefault(atom_lp+num_lp,[]).append(occup_lp) 
            nat_orbs.setdefault(atom_lp+num_lp,[]).append('sp$^{'+p_pl+'}$'+'('+atom_lp+num_lp+')') 

        if "NHO DIRECTIONALITY AND BOND BENDING (deviations from line of nuclear centers)" in outline:
          break
  return(nat_orbs) #  returns a dicconary with nbos as keys and a list of bond attributes as value in a retarded way... Matt Damond


