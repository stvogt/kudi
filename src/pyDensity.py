#! /usr/local/bin

import sys, os
import singlePoint as sp
import operations as op
import cubman 
import commands

class Density:
    def __init__(self, outFile, fchkFile):
        self.outFile = outFile
        self.outPath = os.path.abspath(outFile)
        print self.outPath
        self.fchkFile = fchkFile
        self.fchkpath = os.path.abspath(fchkFile)
        self.lines = op.read_lines(self.outPath)

    def HOMO(self):
        occ_energy_list = sp.get_orbitals(self.lines)[0]
        homo_energy = occ_energy_list[-1]
        homo_number = len(occ_energy_list)
        homo = cubman.generate_cube(homo_number,self.fchkpath, "HOMO.cube",True)
        print "HOMO:  "+str(homo_number) + "  "+homo_energy
        return homo

    def LUMO(self):
        virt_energy_list = sp.get_orbitals(self.lines)[1]
        occ_energy_list = sp.get_orbitals(self.lines)[0]
        lumo_energy = virt_energy_list[0]
        lumo_number = int(len(occ_energy_list)) + 1
        lumo = cubman.generate_cube(lumo_number,self.fchkpath, "LUMO.cube",True)
        print "LUMO:  "+str(lumo_number) + "  "+lumo_energy
        return lumo

    def allCubes(self):
        all_orbs = sp.get_orbitals(self.lines)[2]
        for orbNum in range(1,len(all_orbs)+1):
            cubman.generate_cube(orbNum, self.fchkpath,"cube_"+str(orbNum)+".cub")

    def TotDensity(self,fchk):
        density_cube = fchk.split(".")[0]+".cub"
        f = open("cubdim.dat", "w")
        f.write("-1 -10.0 -10.0 -10.0\n")
        f.write("101 0.2 0.0 0.0\n")
        f.write("101 0.0 0.2 0.0\n")
        f.write("101 0.0 0.0 0.2\n\n")
        f.close()
        input1 = "cubegen 0 density=scf "+fchk+" "+density_cube+" -1 h < cubdim.dat "
        print input1
        os.system(input1)
        #commands.getstatusoutput(input1)
        return density_cube

    def fukuiMinusFD(self,an_fchk):
        print "Computing Fukui minus using Finite Differences"
        fukuiMinus = "fukuiMinusFd.cub"
        neut_cube = self.TotDensity(self.fchkFile)
        an_cube = self.TotDensity(an_fchk)
        FD = cubman.substract_cube(neut_cube,an_cube)
        os.system("mv "+ FD + " "+fukuiMinus)
        return fukuiMinus 

    def fukuiPlusFD(self,cat_fchk):
        print "Computing Fukui plus using Finite Differences"
        fukuiPlus = "fukuiPlusFd.cub"
        neut_cube = self.TotDensity(self.fchkFile)
        cat_cube = self.TotDensity(cat_fchk)
        FD = cubman.substract_cube(cat_cube,neut_cube)
        os.system("mv "+ FD + " "+ fukuiPlus)
        return fukuiPlus 

    def fukuiMinusMartinez(self):
        print "Processing Chi minus.... \n\n"
        occ_orb = sp.get_orbitals(self.lines)[0]
        molecule = self.fchkFile.split("_")[0]
        chiminus=[]
        denocc=0.0
        # Compute the denominator of chimins
        for j in range(1,len(occ_orb)):
            denocc=denocc+float(occ_orb[j])-float(occ_orb[0])	
        # Compute the division to get total chiminus
        for i in range(0,len(occ_orb)):
            chiminus_i = (float(occ_orb[i])-float(occ_orb[0]))/denocc
            chiminus.append(chiminus_i)	
            # Calculo del cubo perteneciente al orbital i-esimo 
            if i==0:
                print "Computing cube for orbital "+str(i)
                cub_sum="F_minus_"+molecule+".cub"
                input1="cubegen 0 MO="+str(i+1)+" "+self.fchkFile+" "+cub_sum+" 0 h" 
                commands.getstatusoutput(input1)
                cubman.sq_cube(cub_sum)
                cubman.mult_cube(cub_sum+"_sq",chiminus_i)

            if i>0:
                print "Computing cube for orbital "+str(i)
                cub_out=molecule+"_"+str(i+1)+".cub"
                input1="cubegen 0 MO="+str(i+1)+" "+self.fchkFile+" "+cub_out+" 0 h" 
                commands.getstatusoutput(input1)
                cubman.sq_cube(cub_out)
                cubman.mult_cube(cub_out+"_sq",chiminus_i)
                cubman.sum_total(cub_sum+"_sq"+"_mult",cub_out+"_sq"+"_mult") 		
        os.system("mv "+cub_sum+"_sq_mult"+" fukuiMinusIAP.cub")
        os.system("rm *cub_sq")
        cub_final = "fukuiMinusIAP.cub"
        return cub_final


    def fukuiPlusMartinez(self):
        print "-----------------------------------------------------------------"
        print "\nProcessing Chi plus.... \n\n"
        occ_orb = sp.get_orbitals(self.lines)[0]
        all_orb = sp.get_orbitals(self.lines)[2]
        molecule = self.fchkFile.split("_")[0]
        chiplus=[] 
        denvirt=0.0 
        # Compute the denominator of chiplus
        start = int(len(occ_orb))
        for j in range(start,len(all_orb)):
          ek_ej = float(all_orb[-1])-float(all_orb[j])
          denvirt= denvirt + ek_ej
        # Compute the division to get total chiplus
        for i in range(start,len(all_orb)):
          chiplus_i=(float(all_orb[-1])-float(all_orb[i]))/denvirt
          chiplus.append(chiplus_i)
 
          if i==start:
            cub_sum="F_plus_"+molecule+".cub"
            input1="cubegen 0 MO="+str(i+1)+" "+self.fchkFile+" "+cub_sum+" 0 h" 
            commands.getstatusoutput(input1)
            cubman.sq_cube(cub_sum)
            cubman.mult_cube(cub_sum+"_sq",chiplus_i)
          if i>start:
            cub_out=molecule+"_"+str(i+1)+".cub"
            input1="cubegen 0 MO="+str(i+1)+" "+self.fchkFile+" "+cub_out+" 0 h" 
            commands.getstatusoutput(input1)
            cubman.sq_cube(cub_out)
            cubman.mult_cube(cub_out+"_sq",chiplus_i)
            cubman.sum_total(cub_sum+"_sq"+"_mult",cub_out+"_sq"+"_mult") 		
        os.system("mv "+cub_sum+"_sq_mult"+" fukuiPlusIAP.cub")
        cub_final = "fukuiPlusIAP.cub"
        return cub_final



    def dualFD(self,cat_fchk,an_fchk):
        if not os.path.exists("duaFD"):
            os.makedirs("dualFD")
        os.chdir("dualFD")
        os.system("cp ../*.fchk .")
        print "About to compute dual descriptor using cation and anion densities "
        dual = cubman.substract_cube(self.fukuiPlusFD(cat_fchk),self.fukuiMinusFD(an_fchk))
        os.system("mv "+dual+" dualFD.cub")
        os.system("rm *.fchk")
        os.chdir("../")

    def dualIAP(self):
        if not os.path.exists("dualIAP"):
            os.makedirs("dualIAP")
        os.chdir("dualIAP")
        os.system("cp ../"+self.fchkFile+" .")
        print "about to compute dual descriptor using Intermediate aproximation "
        dual = cubman.substract_cube(self.fukuiPlusMartinez(), self.fukuiMinusMartinez())
        os.system("mv "+str(dual)+" dualIAP.cub")
        os.system("ls | grep -v 'dual' | grep -v 'fukui' | xargs rm")
        os.chdir("../")

    def dualIAPval(self):
        if not os.path.exists("dualIAPval"):
            os.makedirs("dualIAPval")
        os.chdir("dualIAPval")
        os.system("cp ../"+self.fchkFile+" .")
        print "about to compute dual descriptor using Intermediate aproximation "
        dual = cubman.substract_cube(self.fukuiPlusMartinezVal(), self.fukuiMinusMartinezVal())
        os.system("mv "+str(dual)+" dualIAPval.cub")
        os.system("ls | grep -v 'dual' | grep -v 'fukui' | xargs rm")
        os.chdir("../")

    def dualFMOA(self):
        if not os.path.exists("dualFMOA"):
            os.makedirs("dualFMOA")
        os.chdir("dualFMOA")
        print "about to compute dual descriptor using FMO aproximation"
        dual = cubman.substract_cube(self.LUMO(), self.HOMO())
        os.system("mv "+dual+" dualFMOA.cub")
        os.chdir("../")

    def localHyperSoftnessFMOA(self):
       occ_energy_list = sp.get_orbitals(self.lines)[0]
       HOMO_enr = occ_energy_list[-1]
       virt_energy_list = sp.get_orbitals(self.lines)[1]
       LUMO_energy = virt_energy_list[0]
       hard = float(HOMO_enr) - float(LUMO_energy)
       print "HARDNESS:  " + str(hard)
       if not os.path.exists("lhsFMOA"):
           os.makedirs("lhsFMOA")
       os.chdir("lhsFMOA")
       print "CALCULATING THE DUAL DESCRIPTOR"
       dual = cubman.substract_cube(self.LUMO(), self.HOMO())
       os.system("mv "+dual+" dualFMOA.cub")
       print "MULTIPlYING THE DUAL DESCRIPTOR"
       HS = cubman.mult_cube("dualFMOA.cub", 1.0/(hard*hard))
       os.system("mv "+HS+" lhsFMOA.cub")
       os.chdir("../")

    def orb_save(self,orb_list):
        if not os.path.exists("orbitals"):
            os.makedirs("orbitals")
        os.chdir("orbitals")
        for orb_num in orb_list:
            cubman.generate_cube(orb_num ,"../"+self.fchkFile, ".cub",sq = False)

    #def fukuiPlusMartinezVal(self):
    #    print "-----------------------------------------------------------------"
    #    print "\nProcessing Chi plus Valence.... \n\n"
    #    occ_orb = sp.get_orbitals(self.lines)[0]
    #    all_orb = sp.get_orbitals(self.lines)[2]
    #    atom_list = sp.get_xyz(self.lines)[0]
    #    valence_orbs = op.num_valence_orbs(atom_list)
    #    molecule = self.fchkFile.split("_")[0]
    #    chiplus=[] 
    #    denvirt=0.0 
    #    # Compute the denominator of chiplus
    #    start = int(len(occ_orb))
    #    end = start + int(valence_orbs)
    #    for j in range(start,end):
    #      ek_ej = float(all_orb[-1])-float(all_orb[j])
    #      denvirt= denvirt + ek_ej
    #    # Compute the division to get total chiplus
    #    for i in range(start,end):
    #      print i
    #      chiplus_i=(float(all_orb[-1])-float(all_orb[i]))/denvirt
    #      chiplus.append(chiplus_i)
    #      if i==start:
    #        cub_sum="F_plus_"+molecule+".cub"
    #        input1="cubegen 0 MO="+str(i+1)+" "+self.fchkFile+" "+cub_sum+" 0 h" 
    #        commands.getstatusoutput(input1)
    #        cubman.sq_cube(cub_sum)
    #        cubman.mult_cube(cub_sum+"_sq",chiplus_i)
    #      if i>start:
    #        cub_out=molecule+"_"+str(i+1)+".cub"
    #        input1="cubegen 0 MO="+str(i+1)+" "+self.fchkFile+" "+cub_out+" 0 h" 
    #        commands.getstatusoutput(input1)
    #        cubman.sq_cube(cub_out)
    #        cubman.mult_cube(cub_out+"_sq",chiplus_i)
    #        cubman.sum_total(cub_sum+"_sq"+"_mult",cub_out+"_sq"+"_mult")
    #    os.system("mv "+cub_sum+"_sq_mult"+" fukuiPlusIAPval.cub")
    #    cub_final = "fukuiPlusIAPval.cub"
    #    return cub_final

    #def fukuiMinusMartinezVal(self):
    #    print "Processing Chi minus.... \n\n"
    #    occ_orb = sp.get_orbitals(self.lines)[0]
    #    atom_list = sp.get_xyz(self.lines)[0]
    #    valence_orbs = op.num_valence_orbs(atom_list)
    #    molecule = self.fchkFile.split("_")[0]
    #    chiminus=[]
    #    denocc=0.0
    #    start = int(len(occ_orb)) - int(valence_orbs)
    #    # Compute the denominator of chimins
    #    for j in range(start,len(occ_orb)):
    #        denocc=denocc+float(occ_orb[j])-float(occ_orb[start])
    #    # Compute the division to get total chiminus
    #    for i in range(start,len(occ_orb)):
    #        chiminus_i = (float(occ_orb[i])-float(occ_orb[start]))/denocc
    #        chiminus.append(chiminus_i)
    #        # Calculo del cubo perteneciente al orbital i-esimo 
    #        if i==start:
    #            print "Computing cube for orbital "+str(i)
    #            cub_sum="F_minus_"+molecule+".cub"
    #            input1="cubegen 0 MO="+str(i+1)+" "+self.fchkFile+" "+cub_sum+" 0 h" 
    #            commands.getstatusoutput(input1)
    #            cubman.sq_cube(cub_sum)
    #            cubman.mult_cube(cub_sum+"_sq",chiminus_i)
    #        if i>start:
    #            print "Computing cube for orbital "+str(i)
    #            cub_out=molecule+"_"+str(i+1)+".cub"
    #            input1="cubegen 0 MO="+str(i+1)+" "+self.fchkFile+" "+cub_out+" 0 h" 
    #            commands.getstatusoutput(input1)
    #            cubman.sq_cube(cub_out)
    #            cubman.mult_cube(cub_out+"_sq",chiminus_i)
    #            cubman.sum_total(cub_sum+"_sq"+"_mult",cub_out+"_sq"+"_mult")
    #    os.system("mv "+cub_sum+"_sq_mult"+" fukuiMinusIAPval.cub")
    #    os.system("rm *cub_sq")
    #    cub_final = "fukuiMinusIAPval.cub"
    #    return cub_final
