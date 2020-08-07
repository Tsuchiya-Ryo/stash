
from rdkit import Chem
from rdkit.Chem import AllChem

def mol2dft(x, flag, thread=4, mem=4, input_name="input.py", output_name="output.log", functional="sto-3g", basis="3-21g", method="energy", charge=0, spin=0, gname="GeometryName"):
    
    '''
        *****************************************************************************************************************
        Psi4計算用。
        This function outputs rough atom coordinates of inputted molecule and creates a file for DFT calculation on Psi4.
        Generation of the geometry is based on ETKDGv2.
        (cartesian coordinate)

        rdkit and pubchempy(for searching compound name) must be installed.
        *****************************************************************************************************************
        
        ---Parameters----------------------------------------------------------------------------------------------------
        (int: x, thread, mem, charge, spin)
        (str: flag, input_name, output_name, functional, basis, method, gname)
        
        x: mol/smiles/xyz/compound name
        flag: declare the type of x (= "mol"/"smiles"/"xyz"/"name")
        
        thread: number of cpu threads. Default value is 4
        mem: number of memory assigned(GB unit). Default value is 4
        input_name: the input file name for calculation(actually this function's output name
        output_name: the output file name of calculation log
        functional: default value is "sto-3g"
        basis: default value is "3-21g"
        method: calculation method. default value is "energy"
        charge: default value is 0
        spin: default value is 0
        gname: name of atom coordinates. default value is "GeometryName"
        -----------------------------------------------------------------------------------------------------------------
    '''
    
    if flag not in ["mol", "smiles", "xyz", "name"]:
        print("ArgumentError:\
               \n\tMOL, SMILES, XYZ atom coordinates and Compound name are acceptable.\
               \n\t(flag = 'mol' or 'smiles' or 'xyz' or 'name' must be written.)")
        return
    
    elif flag == "name":
        import pubchempy as pcp

        MOL = pcp.get_compounds(x, "name")
        if not MOL:
            print("The compound name was not found in pubchempy. Try again.")
            return
        else:
            MOL = MOL[0]
            MOL = Chem.MolFromSmiles(MOL.canonical_smiles)
            MOL = Chem.AddHs(MOL)
            AllChem.EmbedMolecule(MOL, AllChem.ETKDGv2())
            XYZ = Chem.rdmolfiles.MolToXYZBlock(MOL)
            XYZ = "\n".join(str(XYZ).splitlines()[2:])

    elif flag == "mol":
        MOL = Chem.AddHs(x)
        AllChem.EmbedMolecule(MOL, AllChem.ETKDGv2())
        XYZ = Chem.rdmolfiles.MolToXYZBlock(MOL)
        XYZ = "\n".join(str(XYZ).splitlines()[2:])
        
    elif flag == "xyz":
        XYZ = "\n".join(str(x).splitlines()[2:])
        
    elif flag == "smiles":
        MOL = Chem.MolFromSmiles(x)
        MOL = Chem.AddHs(MOL)
        AllChem.EmbedMolecule(MOL, AllChem.ETKDGv2())
        XYZ = Chem.rdmolfiles.MolToXYZBlock(MOL)
        XYZ = "\n".join(str(XYZ).splitlines()[2:])
        
    f = open(input_name, "w")
    text = ["import psi4",
            "import datetime",
            "import time",
            "t = datetime.datetime.fromtimestamp(time.time())\n",
            "psi4.set_num_threads(nthread={})".format(int(thread)),
            "psi4.set_memory('{}GB')".format(mem),
            "psi4.set_output_file('{}')".format(str(output_name)),
            "\n{} = psi4.geometry('''".format(gname),
            "{} {}".format(int(charge), int(2*spin+1)),            
            XYZ,
            "''')\n",
            "psi4.{}('{}/{}')".format(method, functional, basis)]
    f.write("\n".join(text))
    f.close

