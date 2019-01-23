import sys
from pathlib import Path
import gaussian_inp

f = open(sys.argv[1],'r').read()

inp = f.split("\n\n")
xyz = inp[0]

inp_d = {}
inp_var = inp[1].split('\n')
for i in range(len(inp_var)):
    if not inp_var[i]:
        break
    inp_d[str(inp_var[i].split("=")[0].strip())] = inp_var[i].split("=")[1].strip()

inp_str = gaussian_inp.irc(inp_d["Method"], inp_d["Basis"], xyz, name=inp_d['Name'],  procs=inp_d['Procs'], mem=inp_d["Mem"], charge=inp_d["Charge"], multi=inp_d["Multiplicity"], maxcycle = inp_d["MaxCycle"], stepsize = inp_d["StepSize"], maxpoints = inp_d["MaxPoints"])

f = open("inp.dat", "w")
f.write(inp_str)
f.close()

