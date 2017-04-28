from parmed.amber import * 
import parmed 

mole = AmberParm("e.prmtop","e.rst7")
sys = AmberParm("SYSTEM.top","SYSTEM.crd")


outputf = open("charge.csv","w")

counter = 0

for at in mole.residues[0].atoms:
    outputf.write("%s,%s,%.4f,%s,%s,%.4f\n" %(sys.residues[0].atoms[counter].name,sys.residues[0].atoms[counter].type,\
                                              sys.residues[0].atoms[counter].charge,\
                                              at.name,at.type,at.charge))
    counter+=1
outputf.close()    
