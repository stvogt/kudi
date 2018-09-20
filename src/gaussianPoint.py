import sys,re,math

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

def get_energy(lines):
  for line in lines:
    if "SCF Done:" in line:
      energy = line.split()[4]
      return energy

def get_last_energy(lines):
  for line in lines:
    if "SCF Done:" in line:
      energy = line.split()[4]
  return energy

def get_scf_cycles(lines):
  for line in lines:
    if "SCF Done:" in line:
      cycles = line.split()[7]
      return cycles

def get_mp2_energy(lines):
    for lineNum in range(0,len(lines)):
        line=lines[lineNum]
        if "EUMP2 =" in line:
            mp2_energy = float(line.split()[5].split("D")[0])*1000.0
            return (mp2_energy, True)
        #elif lineNum==len(lines)-1:
        #    return ("No MP2 energy", False)

def get_casscf_energy(lines):
    for lineNum in range(0,len(lines)):
        line=lines[lineNum]
        if ")     EIGENVALUE" in line:
            casscf_energy = float(line.split()[3])
            return (casscf_energy, True)
        #elif lineNum==len(lines)-1:
        #    return ("No CASSCF energy", False)

def get_corr_energy(lines):
    for lineNum in range(0,len(lines)):
        line=lines[lineNum]
        if "EUMP2 =" in line:
            corr_energy = float(line.split()[2].split("D")[0])
            return corr_energy

def get_orbitals(lines):
  # Obtain iteration range within the output file
  All_energies = []
  for Nline in range(0,len(lines)):
    #if "The electronic state is" in lines[Nline]:
    if "Alpha  occ. eigenvalues" in lines[Nline]:
      startline=Nline
      break
  for Nline in range(0,len(lines)):
    if "Molecular Orbital Coefficients:" in lines[Nline]:
      endline=Nline
      break
    elif "Condensed to atoms"  in lines[Nline]:
      endline=Nline
      break

  # Extract the orbital energies within these lines
  Orbitalenergies_temp=[]
  Virtenergies_temp=[]
  Occenergies_temp=[]

  Orbitalenergies=[]
  Virtenergies=[]
  Occenergies=[]

  for Orbline in range(startline,endline):
    linelist=lines[Orbline].split()
    for lineitem in range(4,len(linelist)):
      orbenergy=linelist[lineitem]
      if "occ." in lines[Orbline]:
        Occenergies_temp.append(orbenergy)
      if "virt." in lines[Orbline]:
        Virtenergies_temp.append(orbenergy)
      Orbitalenergies_temp.append(orbenergy)

  Orbitalenergies=process_occ_energies(Orbitalenergies_temp)
  Virtenergies=process_occ_energies(Virtenergies_temp)
  Occenergies=process_occ_energies(Occenergies_temp)
  return (Occenergies,Virtenergies,Orbitalenergies)


def get_symm_orbs(lines):
    for lineNum in range(0,len(lines)):
        line = lines[lineNum]
        if "Orbital symmetries:" in line:
            occ_symm = []
            virt_symm = []
            Occ_dict = {}
            Virt_dict = {}
            countOrbs = 1
            for lineNum1 in range(lineNum,len(lines)): # First the occupied...
                if "Virtual" in lines[lineNum1]:
                    virtlineNum = lineNum1
                    break
                lineList = lines[lineNum1].split()
                for item in lineList:
                    if "(" in item:
                        orb_symm =item.split("(")[1].split(")")[0]
                        occ_symm.append(orb_symm)
                        Occ_dict[countOrbs] = orb_symm
                        countOrbs = countOrbs + 1
            for lineNum1 in range(virtlineNum,len(lines)):  # Now the virtual orbitals
                if "The electronic state is " in lines[lineNum1]:
                    break
                lineList = lines[lineNum1].split()
                for item in lineList:
                    if "(" in item:
                        orb_symm =item.split("(")[1].split(")")[0]
                        virt_symm.append(orb_symm)
                        Virt_dict[countOrbs] = orb_symm 
                        countOrbs = countOrbs + 1
            # Assigning numbers to each symmetry orbital 
            Occ_dict_num = {}
            Virt_dict_num = {}
            symm_groups = list(set(occ_symm))

            for group in symm_groups:
                count = 1
                for key in Occ_dict.iterkeys():
                   if group == Occ_dict[key]:
                       Occ_dict_num[key] = str(count)+Occ_dict[key]
                       count = count + 1
                for key in Virt_dict.iterkeys():
                   if group == Virt_dict[key]:
                       Virt_dict_num[key] = str(count)+Virt_dict[key]
                       count = count + 1
    all_orbs = get_orbitals(lines)[2]
    count = 1
    orb_dict = {}
    for orb in all_orbs:
        orb_dict[count] = all_orbs[count -1]
        count = count + 1
    return (Occ_dict_num, Virt_dict_num, orb_dict)


def symm_chem_pot(lines):
    all_orb = get_orbitals(lines)[2]
    occ_orb = get_orbitals(lines)[0]
    virt_orb = get_orbitals(lines)[1]
    denocc=0.0
    mu_a1 = 0.0
    occ_symm = get_symm_orbs(lines)[0]
    virt_symm = get_symm_orbs(lines)[1]
    orb_dic = get_symm_orbs(lines)[2]
    symm_dict_occ = {}
    symm_dict_virt = {}
    for key in occ_symm.iterkeys():
        symm_dict_occ[orb_dic[key]] = occ_symm[key]
    for key in virt_symm.iterkeys():
        symm_dict_virt[orb_dic[key]] = virt_symm[key]
    print symm_dict_virt
    # Compute the denominator of chimins
    for j in range(0,len(occ_orb)):
        denocc=denocc+float(occ_orb[j])-float(occ_orb[0])	
    # Compute the division to get total chiminus
    for i in range(0,len(occ_orb)):
        chiminus_i = 0.0
        chiminus_i = (float(occ_orb[i])-float(occ_orb[0]))/(-2*denocc)
        if 'A"' in symm_dict_occ[occ_orb[i]]:
            print occ_orb[i] + "   " + str(chiminus_i)
        #print chiminus_i
        # Obtain the chemical potential
            mu_a1 = mu_a1 + float(occ_orb[i])*chiminus_i
    print "-------------------------------------------"
    denvirt=0.0 
    # Compute the denominator of chiplus
    start = int(len(occ_orb))
    for j in range(start,len(all_orb)):
      ek_ej = float(all_orb[-1])-float(all_orb[j])
      denvirt= denvirt + ek_ej
    # Compute the division to get total chiplus
    for i in range(start,len(all_orb)):
      chiplus_i=(float(all_orb[-1])-float(all_orb[i]))/(-2*denvirt)
      if 'A"' in symm_dict_virt[all_orb[i]]:
        mu_a1 = mu_a1 + float(all_orb[i])*chiplus_i
        print all_orb[i] + "   " + str(chiplus_i)

    mu_kcal = mu_a1*627.51 
    #sys.exit(1)
    return mu_kcal


def get_xyz(lines):
  xyz_info = []
  atoms_num = []
  xyz = []
  x_coords = []
  y_coords = []
  z_coords = []
  found = False
  for lineNum in range(0,len(lines)):
    if "Standard orientation:" in lines[lineNum]:  
      found = True
      for lineNum1 in range(lineNum+5,len(lines)):
        p = re.search('\d+\s*-?\d+.\d+\s*-?\d+.\d+', str(lines[lineNum1]))
        if p: 
          if len(lines[lineNum1].split()) == 5:
            atoms_num.append(lines[lineNum1].split()[1]) # Atom number
            x_coords.append(lines[lineNum1].split()[2])
            y_coords.append(lines[lineNum1].split()[3])
            z_coords.append(lines[lineNum1].split()[4])
          elif len(lines[lineNum1].split()) == 6:
            atoms_num.append(lines[lineNum1].split()[1]) # Atom number
            x_coords.append(lines[lineNum1].split()[3])
            y_coords.append(lines[lineNum1].split()[4])
            z_coords.append(lines[lineNum1].split()[5])
        else:
          xyz.append(atoms_num)
          xyz.append(x_coords)
          xyz.append(y_coords)
          xyz.append(z_coords)
          break
    elif found:
      break
  return xyz



def get_last_xyz(lines):
  xyz_info = []
  atoms_num = []
  x_coords = []
  y_coords = []
  z_coords = []
  for lineNum in range(0,len(lines)):
    #if "Input orientation:" in lines[lineNum]:  
    if "Standard orientation:" in lines[lineNum]:  
      xyz = []
      atoms_num = []
      x_coords = []
      y_coords = []
      z_coords = []
      for lineNum1 in range(lineNum+5,len(lines)):
        p = re.search('\d+\s*-?\d+.\d+\s*-?\d+.\d+', str(lines[lineNum1]))
        if p: 
          if len(lines[lineNum1].split()) == 5:
            atoms_num.append(lines[lineNum1].split()[1]) # Atom number
            x_coords.append(lines[lineNum1].split()[2])
            y_coords.append(lines[lineNum1].split()[3])
            z_coords.append(lines[lineNum1].split()[4])
          elif len(lines[lineNum1].split()) == 6:
            atoms_num.append(lines[lineNum1].split()[1]) # Atom number
            x_coords.append(lines[lineNum1].split()[3])
            y_coords.append(lines[lineNum1].split()[4])
            z_coords.append(lines[lineNum1].split()[5])
        else:
          xyz.append(atoms_num)
          xyz.append(x_coords)
          xyz.append(y_coords)
          xyz.append(z_coords)
          break
  return xyz


def get_level_of_theory(lines):
  inputline_re = re.compile('^\s+?#')
  for lineNum in range(0,len(lines)):
    match = re.search(inputline_re,lines[lineNum])
    if match:
      theory = lines[lineNum].split()[1].split("/")[0]    
      return theory
  print "No level of theory found"
  sys.exit(1)

def get_basis(lines):
  inputline_re = re.compile(r'^\s+?#')
  for lineNum in range(0,len(lines)):
      match = re.search(inputline_re,lines[lineNum])
      if "Standard basis:" in lines[lineNum]:
        basis = lines[lineNum].split()[2]    
        return basis
      if match:
        basis = lines[lineNum].split()[1].split("/")[1]    
        return basis

def get_charge(lines):
  for lineNum in range(0,len(lines)):
      if "Charge =" in lines[lineNum]:
        charge = lines[lineNum].split()[2]    
  return charge

def get_multiplicity(lines):
  for lineNum in range(0,len(lines)):
      if "Multiplicity =" in lines[lineNum]:
        multi = lines[lineNum].split()[5]    
  return multi
