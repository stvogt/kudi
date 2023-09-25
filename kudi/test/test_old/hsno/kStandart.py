
import sys
from kudi import Path

outfile = sys.argv[1]

# Initiate Molecule object
Mol = Path(outfile)

#calculates and prints the reaction works
#works = Mol.ReactionWorks(format_='latex')

# Saves XYZ coordinates in molden text or latex format
Mol.saveXYZ(format_="molden")

# Plot energy profile
energy = Mol.energy()
Mol.savePlot('energy.svg', "Energy",  **energy)
Mol.save("energy.dat",**energy)


# Plot amd save reaction force profile
force = Mol.force()
Mol.savePlot('force.svg',"Reaction Force", **force)
Mol.save("force.dat",**force)

# Plot amd save chemical potential profile
mu = Mol.chemPotKoopman()
Mol.savePlot('chem_pot.svg',r"$\mu(\xi)$", **mu)
Mol.save("chemPot.dat",**mu)

# Plot and save REF
flux_k  = Mol.flux(mu)
Mol.savePlot('flux_k.svg',r"J($\xi$)", **flux_k)
Mol.save("flux.dat",**flux_k)

