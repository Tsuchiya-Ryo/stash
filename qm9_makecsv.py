import bz2
import numpy as np
import pandas as pd
import sys

# python qm9_makecsv.py "./dsgdb9nsd.xyz.bz2"

# I.  Property  Unit         Description
# --  --------  -----------  --------------
#  1  tag       -            "gdb9"; string constant to ease extraction via grep
#  2  index     -            Consecutive, 1-based integer identifier of molecule
#  3  A         GHz          Rotational constant A
#  4  B         GHz          Rotational constant B
#  5  C         GHz          Rotational constant C
#  6  mu        Debye        Dipole moment
#  7  alpha     Bohr^3       Isotropic polarizability
#  8  homo      Hartree      Energy of Highest occupied molecular orbital (HOMO)
#  9  lumo      Hartree      Energy of Lowest occupied molecular orbital (LUMO)
# 10  gap       Hartree      Gap, difference between LUMO and HOMO
# 11  r2        Bohr^2       Electronic spatial extent
# 12  zpve      Hartree      Zero point vibrational energy
# 13  U0        Hartree      Internal energy at 0 K
# 14  U         Hartree      Internal energy at 298.15 K
# 15  H         Hartree      Enthalpy at 298.15 K
# 16  G         Hartree      Free energy at 298.15 K
# 17  Cv        cal/(mol K)  Heat capacity at 298.15 K

filepath = sys.argv[1]
with bz2.open(filepath, "rb") as f:
    allLines = f.read().decode().split("\n")
    f.close()

propertyDict = {}
for i, line in enumerate(allLines):
    if line.startswith("gdb"):
        propertyList = line.split("\t")
        idx = propertyList.pop(0)
        propertyList.pop(-1)
    if line.startswith("InChI"):
        propertyList.insert(0, allLines[i-1].split("\t")[1])
        if len(propertyList) != 16:
            print(f"weirdhchamp: {idx}")
            continue
        else:
            propertyDict[str(idx)] = propertyList
        
df = pd.DataFrame(propertyDict, index=["Smiles","A","B","C","mu","alpha","homo","lumo","gap","r2","zpve","U0","U","H","G","Cv"]).T.reset_index(drop=True)
df[df.columns[df.columns != "Smiles"]] = df[df.columns[df.columns != "Smiles"]].astype(np.float64)

df.to_csv("qm9Property.csv", index=False)
