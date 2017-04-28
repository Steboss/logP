from parmed.amber import * 

base = AmberParm("SYSTEM.top","SYSTEM.crd")

outputf = open("charges.csv","w")

for at in base.residues[0].atoms:
    #at name, charge
    outputf.write("%s, %.4f\n" % (at.name,at.charge))


outputf.close()
