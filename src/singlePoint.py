import sys,re,math
import operations as op
import gaussianPoint as gsp
import orcaPoint as osp

def program(lines):
  for line in lines:
    #if " Gaussian, Inc." in line:
    if "Symbolic Z-matrix:" in line:
        return "G09"
    #if "* O   R   C   A *" or "JOB NUMBER" in line:
    if "JOB NUMBER" in line:
        return "Orca"
    elif line == lines[-1]:
        print "Output file format no supported\nExit"
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

def bonddistance(lines):
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

  for i in range(0,len(atomLabel)-1):
    for j in range(i,len(atomLabel)):
      if i is not j:
        bondLabel.append(atomLabel[i] + str(i+1) + "-" + atomLabel[j] + str(j+1))
        bondDistance.append(math.sqrt((float(xCoord[i])-float(xCoord[j]))**2 + (float(yCoord[i])-float(yCoord[j]))**2 + (float(zCoord[i])-float(zCoord[j]))**2))
  return(bondLabel,bondDistance)

def angles(lines):
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

  for i in range(0,len(atomLabel)-1):
    for j in range(i, len(atomLabel)):
      for k in range(0, len(atomLabel)):
        if i is j:
          continue
        elif i is k:
          continue
        elif j is k:
          continue
        else:
          ex_ki = float(xCoord[k]) - float(xCoord[i])
          ex_kj = float(xCoord[k]) - float(xCoord[j])
          ey_ki = float(yCoord[k]) - float(yCoord[i])
          ey_kj = float(yCoord[k]) - float(yCoord[j])
          ez_ki = float(zCoord[k]) - float(zCoord[i])
          ez_kj = float(zCoord[k]) - float(zCoord[j])
          rki = math.sqrt(ex_ki**2.0 + ey_ki**2.0 + ez_ki **2.0)
          rkj = math.sqrt(ex_kj**2.0 + ey_kj**2.0 + ez_kj **2.0)
          ex_ki = ex_ki/rki
          ey_ki = ey_ki/rki
          ez_ki = ez_ki/rki
          ex_kj = ex_kj/rkj
          ey_kj = ey_kj/rkj
          ez_kj = ez_kj/rkj
          angle.append(180.0/math.pi*math.acos(ex_ki*ex_kj + ey_ki*ey_kj + ez_ki*ez_kj))
          angleLabel.append(atomLabel[i] + str(i+1) + "-" + atomLabel[k] + str(k+1) + "-" + atomLabel[j] + str(j+1))
  return(angleLabel,angle)



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


