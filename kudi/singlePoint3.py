import sys,re,math
import operations3 as op
import gaussianPoint3 as gsp
import orcaPoint3 as osp
import numpy as np

def program(lines):
  for line in lines:
    #if " Gaussian, Inc." in line:
    if "Symbolic Z-matrix:" in line:
        return "G09"
    #if "* O   R   C   A *" or "JOB NUMBER" in line:
    if "JOB NUMBER" in line:
        return "Orca"
    elif line == lines[-1]:
        print("Output file format no supported\nExit")
        return sys.exit(2)

def koopmans(lines):
    if program(lines) == "G09":
      orbs = gsp.get_orbitals(lines)
    if program(lines) == "Orca":
      orbs = osp.get_orbitals(lines)
    homo = float(orbs[0][-1])
    lumo = float(orbs[1][0])
    mu = 0.5*(lumo + homo)*627.509469
    return mu

def finite_diff(ip,ea):
  MU = [] 
  for i in range(0,len(ip)):
    mu = -0.5*(float(ip[i])+float(ea[i]))
    MU.append(mu)
  return MU


def bonddistance(lines,dis_list):
  if program(lines) == "G09":
    xyz = gsp.get_xyz(lines)
    atomLabel = op.atom_label(xyz[0])
  if program(lines) == "Orca":
    xyz = osp.get_xyz(lines)
    atomLabel = xyz[0]
  bondLabel = []
  bondDistance = []
  xCoord = xyz[1]
  yCoord = xyz[2]
  zCoord = xyz[3]
  def distance_calc(i,j):
      label = atomLabel[i] + str(i+1) + "-" + atomLabel[j] + str(j+1)
      bnd_distance = math.sqrt((float(xCoord[i])-float(xCoord[j]))**2 + (float(yCoord[i])-float(yCoord[j]))**2 + (float(zCoord[i])-float(zCoord[j]))**2)
      bondLabel.append(label)
      bondDistance.append(bnd_distance)
      return(bondLabel,bondDistance)

  if dis_list: # If list is not empty, user specified a list of bond lengthes in object definition'
      for bl in dis_list:
          i = int(re.split('(\d+)',bl.split("-")[0])[1])-1
          j = int(re.split('(\d+)',bl.split("-")[1])[1])-1
          dis_info = distance_calc(i,j)
          lab = dis_info[0]
          dis = dis_info[1]
      return (lab,dis)
  else: # If list is empty, user didn't specify a list of bond lengthes in object definition, proceedes to calculate all posible bond distances'
      for i in range(0,len(atomLabel)):
        for j in range(0,len(atomLabel)):
          if i != j:
             dis_info = distance_calc(i,j)
             lab = dis_info[0]
             dis = dis_info[1]
      return (lab,dis)



def angle(lines,ang_list):
  if program(lines) == "G09":
    xyz = gsp.get_xyz(lines)
    atomLabel = op.atom_label(xyz[0])
  if program(lines) == "Orca":
    xyz = osp.get_xyz(lines)
    atomLabel = xyz[0]
  angleLabel = []
  angle = []
  xCoord = xyz[1]
  yCoord = xyz[2]
  zCoord = xyz[3]
  def angle_calc(j,i,k):
      label = atomLabel[j] + str(j+1) + "-" + atomLabel[i] + str(i+1) + "-" + atomLabel[k] + str(k+1)
      v_ij = np.array([float(xCoord[i]) - float(xCoord[j]),float(yCoord[i]) - float(yCoord[j]),float(zCoord[i]) - float(zCoord[j])])
      v_ik = np.array([float(xCoord[i]) - float(xCoord[k]),float(yCoord[i]) - float(yCoord[k]),float(zCoord[i]) - float(zCoord[k])])
      e_ij = np.divide(v_ij,np.linalg.norm(v_ij))
      e_ik = np.divide(v_ik,np.linalg.norm(v_ik))
      theta = 180.0/math.pi*math.acos(np.dot(e_ij,e_ik))
      angle.append(theta)
      angleLabel.append(label)
      return(angleLabel,angle)

  if ang_list:
      for bl in ang_list:
          j = int(re.split('(\d+)',bl.split("-")[0])[1])-1
          i = int(re.split('(\d+)',bl.split("-")[1])[1])-1
          k = int(re.split('(\d+)',bl.split("-")[2])[1])-1
          ang_info = angle_calc(j,i,k)
          ang_lab = ang_info[0]
          ang = ang_info[1]
      return (ang_lab,ang)
  else:
      for i in range(0,len(atomLabel)):
        for j in range(0, len(atomLabel)):
          for k in range(0, len(atomLabel)):
              if i is j:
                  continue
              elif  k is i:
                  continue
              elif k is j:
                  continue
              else:
                  ang_info = angle_calc(j,i,k)
                  ang_lab = ang_info[0]
                  ang = ang_info[1]
      return(ang_lab,ang)

def oop_angle(lines,oop_list):
  if program(lines) == "G09":
    xyz = gsp.get_xyz(lines)
    atomLabel = op.atom_label(xyz[0])
  if program(lines) == "Orca":
    xyz = osp.get_xyz(lines)
    atomLabel = xyz[0]
  oopLabel = []
  oop = []
  xCoord = xyz[1]
  yCoord = xyz[2]
  zCoord = xyz[3]

  def oop_calc(i,j,k,l):
      label = atomLabel[i] + str(i+1) + "-" + atomLabel[j] + str(j+1) + "-" + atomLabel[k] + str(k+1) + "-" + atomLabel[l] + str(l+1)
      v_kl = np.array([float(xCoord[k]) - float(xCoord[l]),float(yCoord[k]) - float(yCoord[l]),float(zCoord[k]) - float(zCoord[l])])
      v_ki = np.array([float(xCoord[k]) - float(xCoord[i]),float(yCoord[k]) - float(yCoord[i]),float(zCoord[k]) - float(zCoord[i])])
      v_kj = np.array([float(xCoord[k]) - float(xCoord[j]),float(yCoord[k]) - float(yCoord[j]),float(zCoord[k]) - float(zCoord[j])])
      e_kl = np.divide(v_kl,np.linalg.norm(v_kl))
      e_ki = np.divide(v_ki,np.linalg.norm(v_ki))
      e_kj = np.divide(v_kj,np.linalg.norm(v_kj))
      theta_jkl = math.acos(np.dot(e_kj,e_kl))
      a = np.dot(np.cross(e_kj,e_kl),e_ki)
      b = math.sin(theta_jkl)
      sin_theta = a/b
      theta = (180.0/math.pi)*math.asin(round(sin_theta,5))
      oop.append(theta)
      oopLabel.append(label)
      return(oopLabel,oop)

  if oop_list:
    for bl in oop_list:
        i = int(re.split('(\d+)',bl.split("-")[0])[1])-1
        j = int(re.split('(\d+)',bl.split("-")[1])[1])-1
        k = int(re.split('(\d+)',bl.split("-")[2])[1])-1
        l = int(re.split('(\d+)',bl.split("-")[3])[1])-1
        oop_info = oop_calc(i,j,k,l)
        oop_lab = oop_info[0]
        oop = oop_info[1]
    return (oop_lab,oop)
  else:
      for i in range(0,len(atomLabel)):
        for j in range(0, len(atomLabel)):
          for k in range(0, len(atomLabel)):
            for l in range(0, len(atomLabel)):
                if i!=j!=k!=l and k!=i!=l!=j:
                      oop_info = oop_calc(i,j,k,l)
                      oop_lab = oop_info[0]
                      oop = oop_info[1]
      return(oop_lab,oop)

def dihedral(lines,dihed_list):
  if program(lines) == "G09":
    xyz = gsp.get_xyz(lines)
    atomLabel = op.atom_label(xyz[0])
  if program(lines) == "Orca":
    xyz = osp.get_xyz(lines)
    atomLabel = xyz[0]
  dihedralLabel = []
  dihedral = []
  xCoord = xyz[1]
  yCoord = xyz[2]
  zCoord = xyz[3]
  def dihedral_calc(i,j,k,l):
      label = atomLabel[i] + str(i+1) + "-" + atomLabel[j] + str(j+1) + "-" + atomLabel[k] + str(k+1) + "-" + atomLabel[l] + str(l+1)
      v_ij = np.array([float(xCoord[i]) - float(xCoord[j]),float(yCoord[i]) - float(yCoord[j]),float(zCoord[i]) - float(zCoord[j])])
      v_jk = np.array([float(xCoord[j]) - float(xCoord[k]),float(yCoord[j]) - float(yCoord[k]),float(zCoord[j]) - float(zCoord[k])])
      v_kl = np.array([float(xCoord[k]) - float(xCoord[l]),float(yCoord[k]) - float(yCoord[l]),float(zCoord[k]) - float(zCoord[l])])
      e_ij = np.divide(v_ij,np.linalg.norm(v_ij))
      e_jk = np.divide(v_jk,np.linalg.norm(v_jk))
      e_kl = np.divide(v_kl,np.linalg.norm(v_kl))
      theta_ijk = math.acos(np.dot(e_ij,e_jk))
      theta_jkl = math.acos(np.dot(e_jk,e_kl))
      cos_delta = (np.dot(np.cross(e_ij,e_jk),np.cross(e_jk,e_kl)))/(math.sin(theta_ijk)*math.sin(theta_jkl))
      delta = (180.0/math.pi)*math.acos(round(cos_delta,5))
      dihedral.append(delta)
      dihedralLabel.append(label)
      return(dihedralLabel,dihedral)

  if dihed_list:
     for bl in dihed_list:
        i = int(re.split('(\d+)',bl.split("-")[0])[1])-1
        j = int(re.split('(\d+)',bl.split("-")[1])[1])-1
        k = int(re.split('(\d+)',bl.split("-")[2])[1])-1
        l = int(re.split('(\d+)',bl.split("-")[3])[1])-1
        dihedral_info = dihedral_calc(i,j,k,l)
        dihedral_lab = dihedral_info[0]
        dihedral = dihedral_info[1]
     return (dihedral_lab,dihedral)
  else:
    for i in range(0,len(atomLabel)):
      for j in range(0, len(atomLabel)):
        for k in range(0, len(atomLabel)):
          for l in range(0, len(atomLabel)):
              if i!=j!=k!=l and k!=i!=l!=j: 
                    dihedral_info = dihedral_calc(i,j,k,l)
                    dihedral_lab = dihedral_info[0]
                    dihedral = dihedral_info[1]
    return (dihedral_lab,dihedral)

def xyz_pretty_print(lines):
    if program(lines) == "G09":
      coords = gsp.get_xyz(lines)
    if program(lines) == "Orca":
      coords = osp.get_xyz(lines)
    XYZ=""
    XYZ_tex=""
    XYZ_molden=""
    for cNum in range(0,len(coords[0])):
        XYZ += '%3s   %15s    %15s   %15s\n' % (coords[0][cNum],coords[1][cNum],coords[2][cNum],coords[3][cNum])
    XYZ += "\n\n"
    # Latex Table generator
    XYZ_tex = '\\begin{center}\n\\begin{tabular}{ c c c c }\n\hline\n'
    for cNum in range(0,len(coords[0])):
          XYZ_tex += '%3s &  %15s  &  %15s &  %15s \\\\ \n' % (coords[0][cNum],coords[1][cNum],coords[2][cNum],coords[3][cNum])
    XYZ_tex += "\hline\n \end{tabular}\n \end{center}"
    # Molden Format generator
    for cNum in range(0,len(coords[0])):
        if program(lines) == "G09":
            XYZ_molden += '%3s   %15s    %15s   %15s\n' % (op.Num2atom(coords[0][cNum]),coords[1][cNum],coords[2][cNum],coords[3][cNum])
        if program(lines) == "Orca":
            XYZ_molden += '%3s   %15s    %15s   %15s\n' % (coords[0][cNum],coords[1][cNum],coords[2][cNum],coords[3][cNum])
    return (XYZ,XYZ_tex,XYZ_molden)


