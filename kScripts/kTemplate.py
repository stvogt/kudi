#! /usr/bin/python

import sys
from kudi import Path

outfile = sys.argv[1]

##Initiate molecule object
Mol = Path(outfile)

#Call the oribital object and save the resulting diccionarry in all_orbitals
all_orbitals = Mol.all_orbtitals()

# Do the same for al intramolecular distances and angles
distances = Mol.distances()
angles = Mol.angels()

#If the output contains a NBO calculation

wibBndIDX = Mol.bondOrders()
natCharges = Mol.natCharges()
bndOrbs = Mol.bondOrbital()

#If your supermolecule contains Symmetry you can extract the symmetry orbitals (only G09)

symm_orbitals = Mol.symm_orbitals()
Mol.savePlotProp("orbitals_4A1.svg","Occ. Orbs.",["4A1"], **symm_orbitals)

# Plot the orbtials contained in your porperties list, you need to look them in your input. Python starts counting at 0

Mol.savePlotProps("MOs.svg","Energy",['53','54','55','56'], bullets=['ro','bo','g-','k^'],  **all_orbitals)
Mol.save("MOs.dat", prop_list=['56','54'], **all_orbitals)

Mol.savePlotPropsCuts('test.svg','Occ. Orbs.',['53','54','55'],limit_list1=[-0.3,-0.2],limit_list2=[-0.1,0.0],work=True, **all_orbitals)
Mol.savePlotPropsCuts("test.svg","Occ. Orbs.",['53','54'],bullets=['ro','bo','g-','k^'],  **all_orbitals)


# Plot Force and and orbital in the same plot
force = Mol.force()
orbital = Mol.porperties(['54'], **all_orbitals)
plot_list = [force,orbital]
Mol.savePlotMultiScale("multi.svg","kcal/mol", 'hartrees',plot_list)


# Plot amd save chemical poa2tential profile with symmetry orbitals
mu1 = Mol.chemPotGeneral("4A1","5A1")
Mol.savePlot('chem_pot_A1',"\mu", **mu1)
flux1  = Mol.flux(mu1)
Mol.savePlot('flux_A1.svg',"REF ", **flux1)


#Obtain Bond order derivatives
bnd_der = Mol.bondOrderDeriv()
Mol.save("bndordder.dat", **bnd_der)
Mol.savePlotProp("BondOrderDer.png","Bond Order",["S2-C3","C3-O4"], **bnd_der)

#Obtain Bond distances
#distances = Mol.distances()
#Mol.save("distances.dat", **distances)
#Mol.savePlotProp("Distance_SNO.svg","Distances",["S2-N3","N3-O4"] ,True, **distances)

#Obtain Angles
#angles = Mol.angles()
#Mol.save("angels.dat", **angles)
#Mol.savePlotProp("angles.png","Distances",["C1-F6-H4", "C1-F5-H4"] ,True, **angles)

#Obtain atomic natural charges
#charges = Mol.natCharges()
#Mol.save("charges.dat", **charges)
#Mol.savePlotProp("Charges_SNO.svg","Natural Charge",["S2","N3","O4"] ,True, **charges)


