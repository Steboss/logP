from parmed.amber import * 
import parmed

base = AmberParm("SYSTEM.top","SYSTEM.crd")
parmed.tools.writeFrcmod(base,"a.frcmod").execute()
parmed.tools.writeOFF(base,"a.off").execute()
