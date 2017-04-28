from parmed.amber import * 
import parmed


orig = AmberParm("../off_frcmod/SYSTEM.top","../off_frcmod/SYSTEM.crd")
new = AmberParm("../test.prmtop","../test.rst7")

outputf = open("compare.csv", "w")

counter = 0 
ligand = orig.residues[0]

for at in ligand.atoms:
    #name,type, charge
    #remember we have re-mapped the atoms
    outputf.write("%s, %s, %.4f, ,%s,%s,%.4f\n" % (at.name,at.type,at.charge,\
	 					 new.residues[0].atoms[counter].name,new.residues[0].atoms[counter].type,\
                                                 new.residues[0].atoms[counter].charge) )
    counter+=1

 
outputf.close()

outputf=open("bond_compare.csv","w")

counter = 0 

for at in new.residues[0].atoms:
    #at, bonds
    for bond in at.bonds:
        outputf.write("%s,%s,%.4f\n" % ( bond.atom1,bond.atom2,bond.type.req))

outputf.close()
