#! /usr/bin/python

import sys, os, glob, random
import pathEngine
import gaussianPoint as gsp
import orcaPoint as osp
import singlePoint as sp
import operations as op
import nbo
from pyDensity import Density
#from termcolor import colored

class Path:
  def __init__(self, outfile, *argv):
    self.outfile = outfile
    self.outpath = os.path.abspath(outfile)
    self.lines = op.read_lines(outfile)
    self.blocks = pathEngine.get_blocks(self.lines)
    try: 
        self.out_cat = argv[0]
        self.lines_cat = op.read_lines(out_cat)
        self.blocks_cat = pathEngine.get_blocks(self.lines_cat)
    except IndexError:
        pass
    try: 
        self.out_an = argv[1]
        self.lines_an = op.read_lines(out_an)
        self.blocks_an = pathEngine.get_blocks(self.lines_an)
    except IndexError:
        pass


  def program(self):
    return sp.program(self.lines)

  def rxCoord(self):
    rx_coord = pathEngine.get_rxCoord(self.lines)  
    return rx_coord

  def energy(self,relative=True):
    if self.program() == "G09":
        energy = pathEngine.extract_from_blocks(gsp.get_energy, self.blocks)
    if self.program() == "Orca":
        energy = pathEngine.extract_from_blocks(osp.get_energy, self.blocks)
    if relative:
        energy[:] = [(float(x) - float(energy[0]))*627.509469 for x in energy]
    return {"Reaction Coordinate": self.rxCoord(), "Energy":energy}

  def energy_mp2(self):
    energy = pathEngine.extract_from_blocks(gsp.get_mp2_energy, self.blocks)
    energy[:] = [(float(x) - float(energy[0]))*627.509469 for x in energy]
    return {"Reaction Coordinate": self.rxCoord(), "Energy":energy}

  def energy_casscf(self):
    energy = pathEngine.extract_from_blocks(gsp.get_casscf_energy, self.blocks)
    energy[:] = [(float(x) - float(energy[0]))*627.509469 for x in energy]
    return {"Reaction Coordinate": self.rxCoord(), "Energy":energy}

  def corr_energy(self):
    energy = pathEngine.extract_from_blocks(gsp.get_corr_energy, self.blocks)
    return {"Reaction Coordinate": self.rxCoord(), "Energy":energy}

  def force(self,smooth=False):
    if not smooth:
        coord = op.neg_derivative(self.rxCoord(),self.energy()['Energy'])[0]
        force = op.neg_derivative(self.rxCoord(),self.energy()['Energy'])[1]
    if smooth:
        coord = op.neg_derivative_smooth(self.rxCoord(),self.energy()['Energy'])[0]
        force = op.neg_derivative_smooth(self.rxCoord(),self.energy()['Energy'])[1]
    return {"Reaction Coordinate":coord , "Reaction Force":force}

  def distances(self):
    print "----Distances---"
    sigma = []
    Sigma = {}
    all_dis = pathEngine.extract_from_blocks(sp.bonddistance,self.blocks)
    num_dist = len(all_dis[0][0])
    Sigma["Reaction Coordinate"] = self.rxCoord()
    for j in range(0, num_dist):
      for coord in range(0,len(all_dis)):
        sigma.append(all_dis[coord][1][j])
      Sigma[all_dis[0][0][j]] = sigma
      print all_dis[0][0][j]
      sigma = []
    return Sigma

  def angles(self):
    print "----Angles---"
    sigma = []
    Sigma = {}
    all_angles = pathEngine.extract_from_blocks(sp.angles,self.blocks)
    num_ang = len(all_angles[0][0])
    Sigma["Reaction Coordinate"] = self.rxCoord()
    for j in range(0, num_ang):
      for coord in range(0,len(all_angles)):
        sigma.append(all_angles[coord][1][j])
      Sigma[all_angles[0][0][j]] = sigma
      print all_angles[0][0][j]
      sigma = []
    return Sigma

  def bondOrders(self):
    Bndo = {}
    bndo_list = []
    bondOrder = pathEngine.extract_from_blocks(nbo.bondOrder,self.blocks)
    rx_coord = self.rxCoord()
    Bndo["Reaction Coordinate"] = rx_coord
    print "----------- Bonds ----------"
    for key in bondOrder[0]:
      print key
      for coord_num in range(0,len(rx_coord)):
        dicts = bondOrder[coord_num]
        bndo_list.append(dicts[key])
      Bndo[key] = bndo_list  
      bndo_list = []
    return Bndo

  def natCharges(self):
    Charges = {}
    charges_list = []
    charges =  pathEngine.extract_from_blocks(nbo.natCharges,self.blocks)
    rx_coord = self.rxCoord()
    Charges["Reaction Coordinate"] = rx_coord
    print "------------Charges-------------"
    for key in charges[0]:
      print key
      for coord_num in range(0,len(rx_coord)):
        dicts = charges[coord_num]
        charges_list.append(dicts[key])
      Charges[key] = charges_list  
      charges_list = []
    return Charges

  def bondOrbital(self):
    pathEngine.all_bondOrbitals(self.blocks)

  def occ_orbitals(self):
    if self.program() == "G09":
        all_orbs = pathEngine.extract_from_blocks(gsp.get_orbitals, self.blocks)
    if self.program() == "Orca":
        all_orbs = pathEngine.extract_from_blocks(osp.get_orbitals, self.blocks)
    #all_orbs = pathEngine.all_orbs(self.blocks)
    val_orbs = op.num_valence_orbs(self.atoms())
    epsilon = []
    Epsilon = {}
    num_orbs = len(all_orbs[0][0])
    Epsilon["Reaction Coordinate"] = self.rxCoord()
    end = num_orbs
    start = num_orbs - val_orbs
    for j in range(start,end):
      for coord in range(0,len(all_orbs)):
        epsilon.append(all_orbs[coord][0][j])
      Epsilon[str(j)] = epsilon
      epsilon = []
    return Epsilon

  def virt_orbitals(self):
    if self.program() == "G09":
        all_orbs = pathEngine.extract_from_blocks(gsp.get_orbitals, self.blocks)
    if self.program() == "Orca":
        all_orbs = pathEngine.extract_from_blocks(osp.get_orbitals, self.blocks)
    #all_orbs = pathEngine.all_orbs(self.blocks)
    val_orbs = op.num_valence_orbs(self.atoms())
    epsilon = []
    Epsilon = {}
    num_orbs = len(all_orbs[0][1])
    Epsilon["Reaction Coordinate"] = self.rxCoord()
    end = val_orbs
    start = 1
    for j in range(start,end):
      for coord in range(0,len(all_orbs)):
        epsilon.append(all_orbs[coord][1][j])
      Epsilon[str(j)] = epsilon
      epsilon = []
    return Epsilon

  def all_orbtitals(self):
    if self.program() == "G09":
        all_orbs = pathEngine.extract_from_blocks(gsp.get_orbitals, self.blocks)
        start = 1
    if self.program() == "Orca":
        all_orbs = pathEngine.extract_from_blocks(osp.get_orbitals, self.blocks)
        start = 0
    epsilon = []
    Epsilon = {}
    num_orbs = len(all_orbs[0][2])
    Epsilon["Reaction Coordinate"] = self.rxCoord()
    for j in range(start, num_orbs):
      for coord in range(0,len(all_orbs)):
        epsilon.append(all_orbs[coord][2][j])
      Epsilon[str(j)] = epsilon
      epsilon = []
    return Epsilon

  def HOMO_LUMO(self):
    if self.program() == "G09":
        all_orbs = pathEngine.extract_from_blocks(gsp.get_orbitals, self.blocks)
        start = 1
    if self.program() == "Orca":
        all_orbs = pathEngine.extract_from_blocks(osp.get_orbitals, self.blocks)
        start = 0
    HOMO = []
    LUMO = []
    HOMO_LUMO = {}
    HOMO_LUMO["Reaction Coordinate"] = self.rxCoord()
    for coord in range(0,len(all_orbs)):
      HOMO.append(all_orbs[coord][0][-1])
      LUMO.append(all_orbs[coord][1][0])
    HOMO_LUMO["HOMO"] = HOMO
    HOMO_LUMO["LUMO"] = LUMO
    return HOMO_LUMO

  def porperties(self,prop_list,**kwargs):
    prop_dict ={}
    for key in kwargs.keys():
        if key != 'Reaction Coordinate':
            if key in prop_list:
                prop_dict[key]= kwargs[key]
        if key == 'Reaction Coordinate':
                prop_dict[key]= kwargs[key]
    return prop_dict


  def symm_orbitals(self):
      symm_orbs_all = pathEngine.all_symm_orbs_energ(self.blocks)[0]
      symm_orbs_occ = gsp.get_symm_orbs(self.lines)[0]
      symm_orbs_virt = gsp.get_symm_orbs(self.lines)[1]
      print "\nSymmetries of occupied orbitals:"
      for key in sorted(symm_orbs_occ.iterkeys()):
          print str(key) +":  "+ symm_orbs_occ[key]
      count = 0
      print "\nSymmetries of occupied orbitals:"
      for key in sorted(symm_orbs_virt.iterkeys()):
          print str(key) +":  "+ symm_orbs_virt[key]
          count = count +1
          if count == 5:
              break
      print "###########################################"
      symm_orbs_all["Reaction Coordinate"] = self.rxCoord()
      return symm_orbs_all

  def chemPotKoopman(self):
    #chemPot = pathEngine.all_koopmans(self.blocks)
    chemPot = pathEngine.extract_from_blocks(sp.koopmans, self.blocks)
    return {"Reaction Coordinate": self.rxCoord(), "Chemical Potential":chemPot}

  def chemPotSymm(self):
    chemPot = pathEngine.extract_from_blocks(gsp.symm_chem_pot, self.blocks)
    return {"Reaction Coordinate": self.rxCoord(), "Chemical Potential":chemPot}

  def chemPotGeneral(self,orbOcc,orbVirt):
    chemPotGen = []
    orbs = pathEngine.all_symm_orbs_energ(self.blocks)[0]
    orbOcc_enrg = orbs[orbOcc]
    orbVirt_energ= orbs[orbVirt]
    for i in range(0,len(orbOcc_enrg)):
        mu = 0.5*(float(orbOcc_enrg[i]) + float(orbVirt_energ[i]))*627.5095
        chemPotGen.append(mu)
    return {"Reaction Coordinate": self.rxCoord(), "Chemical Potential":chemPotGen}

  def flux(self, chemPot, smooth=False):
    if smooth:
        coord = op.neg_derivative_smooth(self.rxCoord(),chemPot['Chemical Potential'])[0]
        flux  = op.neg_derivative_smooth(self.rxCoord(),chemPot['Chemical Potential'])[1]
    if not smooth:
        coord = op.neg_derivative(self.rxCoord(),chemPot['Chemical Potential'])[0]
        flux  = op.neg_derivative(self.rxCoord(),chemPot['Chemical Potential'])[1]
    return {'Reaction Coordinate':coord, 'REF' : flux}

  def bondOrderDeriv(self):
    bondOrder = self.bondOrders()
    der_dict = {}
    for order in bondOrder:
      if order != "Reaction Coordinate":
        neg_der = op.neg_derivative(self.rxCoord(),bondOrder[order])
        der_dict[order] = neg_der[1]
        der_dict["Reaction Coordinate"] = neg_der[0]
    return der_dict
      
  #def IP(self, outfile_cat):
  #  I = []
  #  for enrg_item in range(0,len(cat_enrg)):
  #      ip = float(cat_enrg[enrg_item])-float(neut_enrg[enrg_item])
  #      I.append(ip)
  #      ip = pathEngine.get_IP(self.lines,cat_lines)
  #  return {"Reaction Coordinate": self.rxCoord(), "IP":ip}
  #  
  #def EA(self, outfile_an):
  #  ea = pathEngine.get_EA(self.lines,an_lines)
  #  return {"Reaction Coordinate": self.rxCoord(), "EA":ea}

  def chemPotFinitDiff(self,ip, ea):
    chemPotFD = sp.finite_diff(ip['IP'], ea['EA'])
    return {"Reaction Coordinate": self.rxCoord(), "Chemical Potential":chemPotFD}

  def simplePlot(self,x,y):
    return op.simple_plot(x,y)

  def savePlot(self,plotname, ylabel, limit_list=None, interval=None, bullets = None, work=False, zeroline=False, Show=False,  **kwargs):
    print "Generating the plot with the savePlot..."
    if not bullets:
        bullets = ['bo',  'rs', 'k^', 'b-', 'm-.','bo',  'rs', 'k^', 'g-', 'm-.']
    if not os.path.isdir("figures"):
      os.makedirs("figures")
    os.chdir("figures")
    if work:
        works = self.ReactionWorks()
    else:
        works = []
    op.general_plot(plotname, ylabel, limit_list, interval, bullets, works, zeroline, Show, **kwargs)
    os.chdir("../")

  def savePlotMulti(self,plotname, ylabel, prop_list, work=False, zeroline=False, Show=False, limit_list=None, interval=None, bullets = None):
    print "Generating the plot with the savePlotMulti..."
    if not bullets:
        bullets = ['bo',  'rs', 'k^', 'b-', 'm-.','bo',  'rs', 'k^', 'g-', 'm-.']
    if not os.path.isdir("figures"):
      os.makedirs("figures")
    os.chdir("figures")
    if work:
        works = self.ReactionWorks()
    else:
        works = []
    op.plot_multi(plotname, ylabel, prop_list, limit_list, interval, bullets, works, zeroline, Show)
    os.chdir("../")

  def savePlotMultiScale(self,plotname, ylabel1, ylabel2, dictos, limit_list1=None, limit_list2=None, interval1=None, interval2=None, bullets = None, work=False, zeroline=False, Show=False):
    print "Generationg the plot with the savePlotMultiScale..."
    if not bullets:
        bullets = ['bo',  'rs', 'k^', 'b-', 'm-.','bo',  'rs', 'k^', 'g-', 'm-.']
    if not os.path.isdir("figures"):
      os.makedirs("figures")
    os.chdir("figures")
    if work:
        works = self.ReactionWorks()
    else:
        works = []
    op.general_plot_scales(plotname, ylabel1, ylabel2, dictos, limit_list1, limit_list2, interval1, interval2, bullets, works, zeroline, Show)
    os.chdir("../")

  def savePlotProps(self,plotname, ylabel, proplist, limit_list=None, interval=None, bullets=None, work=False, zeroline=False, Show=False, **kwargs):
    print "Generating the plot with the savePlotProps..."
    if not bullets:
      bullets = ['bo',  'rs', 'k^', 'b-', 'm-.','bo',  'rs', 'k^', 'g-', 'm-.']
    if len(bullets) < len(proplist):
        #print colored('Error: You need to specify more bullet styles and colors','red')
        print 'Error: You need to specify more bullet styles and colors'
        sys.exit(1)
    if not os.path.isdir("figures"):
      os.makedirs("figures")
    os.chdir("figures")
    if work:
        works = self.ReactionWorks()
    else:
        works = []
    op.general_plot_props(plotname, ylabel, proplist, limit_list, interval, bullets,  works, zeroline, Show, **kwargs)
    os.chdir("../")

  def savePlotPropsCuts(self,plotname, ylabel, proplist, limit_list1=None, limit_list2=None, interval1=None, interval2=None, bullets=None, work = False, Show=False, **kwargs):
    print "Generating the plot with the savePlotPropsCuts "
    if not bullets:
      bullets = ['bo',  'rs', 'k^', 'b-', 'm-.','bo',  'rs', 'k^', 'g-', 'm-.']
    if not limit_list1 and limit_list2:
        #print colored("You need to specify the limits for both intervals, e.g.:\nMol.savePlotPropsCuts('test.svg','Occ. Orbs.',['53','54'],limit_list1=[-0.3,-0.2],limit_list2=[-0.1,0.0], **all_orbitals) ",'red')
        print "You need to specify the limits for both intervals, e.g.:\nMol.savePlotPropsCuts('test.svg','Occ. Orbs.',['53','54'],limit_list1=[-0.3,-0.2],limit_list2=[-0.1,0.0], **all_orbitals) "
        sys.exit(2)
    if not os.path.isdir("figures"):
      os.makedirs("figures")
    os.chdir("figures")
    if work:
        works = self.ReactionWorks()
    else:
        works = []
    op.general_plot_prop_with_cuts(plotname, ylabel, proplist, limit_list1, limit_list2, interval1, interval2, bullets,  works, Show, **kwargs)
    os.chdir("../")

  def save(self, filename, prop_list=None,  **kwargs):
    print "Saving the data in: "+filename
    print '----------------------------------------------------------'
    if not os.path.isdir("data"):
      os.makedirs("data")
    os.chdir("data")
    if not prop_list:
        op.general_print(filename, **kwargs)
    if prop_list:
        for key in kwargs.keys():
            if key != 'Reaction Coordinate':
                if key not in prop_list:
                    del kwargs[key]
        op.general_print(filename, **kwargs)
    os.chdir("../")

  def saveXYZ(self,format_='molden'):
    print "Saving XYZ info in "+format_+" format"
    print '----------------------------------------------------------'
    if not os.path.isdir("data"):
      os.makedirs("data")
    os.chdir("data")
    energy = self.energy()
    pathEngine.get_all_xyz(self.blocks, energy["Reaction Coordinate"], energy["Energy"], format_)
    os.chdir("../")

  def ReactionWorks(self,format_='text'):
    y_in = self.force()["Reaction Force"]
    x_in = self.force()["Reaction Coordinate"]
    if float(x_in[0]) > 0:
      x = x_in[::-1] 
      y = y_in[::-1] 
    else: 
      x = x_in 
      y = y_in 
    max_force = max(y)
    min_force = min(y)

    for i in range(0,len(y)):
      if y[i] == min_force:
        w1_cut = i
        w1_rxcoord = x[w1_cut]
      elif y[i] == max_force:
        w3_cut = i
        w3_rxcoord = x[w3_cut]

    for i in range(5,len(y)): # To avoid numerical imprecisions in point 0 and 1
      if y[i] > 0.0:
        w2_cut = i-1
        w2_rxcoord = x[w2_cut]
        break

    w1_y = y[:w1_cut+1]
    w1_x = x[:w1_cut+1]
    w2_y = y[w1_cut:w2_cut+1] ## Due to python list handling
    w2_x = x[w1_cut:w2_cut+1]
    w3_y = y[w2_cut:w3_cut+1]
    w3_x = x[w2_cut:w3_cut+1]
    w4_y = y[w3_cut:]
    w4_x = x[w3_cut:]

    w1 = round(-1.0*(op.integrate(w1_x,w1_y)),2)
    w2 = round(-1.0*(op.integrate(w2_x,w2_y)),2)
    w3 = round(-1.0*(op.integrate(w3_x,w3_y)),2)
    w4 = round(-1.0*(op.integrate(w4_x,w4_y)),2)
    if not os.path.isdir("data"):
      os.makedirs("data")
    os.chdir("data")
    if format_ == 'text':
          f = open('works.dat','w')
          f.write("W1     W2       W3       W4\n")
          f.write(str(w1)+"    "+str(w2)+"    "+str(w3)+"    "+str(w4)+"    ")
          f.close
    if format_ == 'latex':
          f = open('works.tex','w')
          XYZ_tex = '\\begin{center}\n\\begin{tabular}{ |c c | c c c c| }\n\hline\n'
          XYZ_tex += '%4s  & %4s  & %4s &  %4s  &  %4s &  %4s \\\\\hline \n' % ("$\Delta E^0$","$\Delta E^{\ddagger}$","W$_{1}$","W$_{2}$","W$_{3}$","W$_{4}$")
          XYZ_tex += '%4.2f & %4.2f & %4.2f &  %4.2f  &  %4.2f &  %4.2f \\\\ \n' % (w1+w2+w3+w4,w1+w2,w1,w2,w3,w4)
          XYZ_tex += "\hline\n \end{tabular}\n \end{center}"
          f.write(XYZ_tex)
          f.close()
    os.chdir("../")
    return (w1,w2,w3,w4,w1_rxcoord,w3_rxcoord)

  def generate_cube_file(self,orb_range):
    atom_list = self.atoms()
    op.cube_files(orb_range,atom_list, self.lines)

  def dual(self):
    if not os.path.isdir("density"):
        os.makedirs("density")
    op.fchk_gen("CHK")
    for file_ in glob.glob("CHK/*.fchk"):
        density =  Density(self.outfile, file_)
        os.chdir("density")
        density.dualFMOA()
        destiny  = "dualFMOA_"+file_.split("_")[1].split(".")[0]+".cub"
        print destiny
        os.system("mv dualFMOA/dualFMOA.cub dualFMOA/"+destiny)
        os.chdir("../")


