#DEC 2016 Stefano Bosisio
#creation of a  new systemw ith parmed.py
#usage: python parmed_system.py  TOP  CRD  top_ion crd_ion CUDA_IDX  Howmanyions?
import parmed
from parmed.amber import *
import os,sys,math,time,subprocess,random


def tleapdat(mol2_file):
    r""" tleapdat: Function to create the tleap inputfile for solvation process

    Parameters
    ----------
    mol2_file : Input mol2 file to be solvated


    Returns
    -------
    tleap.dat : .dat file which can be read by tleap via tleap -f tleap.dat

    """

    tleap_file = open("tleap.dat","w")
    tleap_file.write("""source leaprc.gaff
loadoff ../../cyclohexane/cyc.off
mol = loadmol2 %s
solvatebox mol CYC 20.0 0.75 iso
saveamberparm mol solvated.parm7 solvated.rst7
quit""" %mol2_file)
    tleap_file.close()


def parmed_add(mol2_file): # ,cuda_index):
    r""" parmed_add: Function for adding a water box to mol2_file

    Parameters
    ----------
    mol2_file : Input mol2 file to be solvated

    cuda_index: int index of the GPU to run MD

    Returns
    -------
    prmtop, rst7 : topology and coordinate files

    """
    print("preparing tleap inputfile")
    tleapdat(mol2_file)
    print("Running tleap")
    cmd ="tleap -f tleap.dat"
    print(cmd)
    os.system(cmd)

    print("Equilibration")

    if not os.path.exists("equilibration"):
        os.makedirs("equilibration")
#    if not os.path.exists("equilibration/md_sire"):#
#        os.makedirs("equilibration/md_sire")

    cmd= "mv solvated.*  equilibration/."
    os.system(cmd)
    #change directory since we will work into equilibration
    os.chdir("equilibration")

    equilibration()


def sander_files():
    r""" sander_files: Run an equilibration protocol with sander

    Parameters
    ----------

    Returns
    -------

    """
    #WARNING: here we have to add ntxo=1 to the input because Amber16 save in NetCFD automatically
    print("Creating sander files")
    min00001_file = open("min00001.in","w")
    min00001_file.write('''
Minimise whole system
&cntrl
ntxo=1,
imin = 1, ntmin = 1,
maxcyc = 100, ncyc = 10,
ntpr = 20, ntwe = 20,
dx0 = 1.0D-7,
ntb = 1,
ntr = 1, restraint_wt = 10.00,
restraintmask="!:CYC",
/
'''
    )

    md00002_file = open("md00002.in","w")
    md00002_file.write('''heat the system
&cntrl
ntxo=1,
imin = 0, nstlim = 1000, irest = 0, ntx = 1, dt = 0.002,
nmropt = 1,
ntt = 1, temp0 = 300.0, tempi = 5.0, tautp = 1.0,
ntb = 1, pres0 = 1.0,
ntc = 2, ntf = 2,
ioutfm = 1, iwrap = 1,
ntwe = 200, ntwx = 200, ntpr = 100,
ntr = 1, restraint_wt = 10.00,
restraintmask="!:CYC",
/

&wt
type = 'TEMP0',
istep1 = 0, istep2 = 1000,
value1 = 5.0, value2 = 300.0
/

&wt type = 'END'
 /
 ''')

    md00003_file = open("md00003.in","w")
    md00003_file.write('''constant temperature
&cntrl
ntxo=1,
imin = 0, nstlim = 4000, irest = 1, ntx = 5, dt = 0.002,
ntt = 1, temp0 = 300.0, tautp = 1.0,
ntb = 1,
ntc = 2, ntf = 2,
ioutfm = 1, iwrap = 1,
ntwe = 800, ntwx = 800, ntpr = 400,
ntr = 1, restraint_wt = 10.00,
restraintmask="!:CYC",
/
 ''')

    md00004_file = open("md00004.in","w")
    md00004_file.write('''md with sander
&cntrl
ntxo=1,
imin = 0, nstlim = 15000, irest = 1, ntx = 5, dt = 0.002,
ntt = 1, temp0 = 298.0, tautp = 1.0,
ntp = 1, pres0 = 1.0, taup = 0.5,
ntb = 2,
ntc = 2, ntf = 2,
ioutfm = 1, iwrap = 1,
ntwe = 3000, ntwx = 3000, ntpr = 1500,
ntr = 1, restraint_wt = 10.00,
restraintmask="!:CYC",
/
 ''')
    min00001_file.close()
    md00002_file.close()
    md00003_file.close()
    md00004_file.close()

    print("Created all the in files for sander")


def equilibration():
    r""" equilibration: instructions to equilibrate the new system
    parm7 and rst7 will be copy into a new equilibration/ folder
    there equilibration will be run in sander

    Parameters
    ----------

    Returns
    -------
    """

    wherearewe = os.getcwd()
    print("now we are here")
    print(wherearewe)

    sander_files()

    print("Minimisation")
    cmd = "sander -i min00001.in -p solvated.parm7 -c solvated.rst7 -O -o min00001.out -e min00001.en -x min00001.nc -inf min00001.info -r min00001.rst7 -ref solvated.rst7"
    os.system(cmd)
    os.system("wait")
    #creation = True
    #while(creation):
#        if os.path.isfile("solvated.rst7"):#
#            creation = True
#        else:
#            creation = False

    print("Equilibration")
    cmd = "sander -i md00002.in -p solvated.parm7 -c min00001.rst7 -O -o md00002.out -e md00002.en -x md00002.nc -inf md00002.info -r md00002.rst7 -ref solvated.rst7"
    os.system(cmd)
    os.system("wait")

    print("Pressure control")
    cmd = "sander -i md00003.in -p solvated.parm7 -c md00002.rst7 -O -o md00003.out -e md00003.en -x md00003.nc -inf md00003.info -r md00003.rst7 -ref solvated.rst7"
    os.system(cmd)
    os.system("wait")

#    print("MD sander")
#    cmd = "sander -i md00004.in -p solvated.parm7 -c md00003.rst7 -O -o md00004.out -e md00004.en -x md00004.nc -inf md00004.info -r md00004.rst7 -ref solvated.rst7"
#    os.system(cmd)
#    os.system("wait")

    #now we have create all the files
    cmd = "cp solvated.parm7 md00003.rst7 ../."
    os.system(cmd)
    print("Created solvated.parm7 and md00004.rst7")

    #Once it's finished we need to call Sire ina new folder and running a fast MD
    #then extract rst7

#    cmd = "cp md00003.rst7  solvated.parm7  md_sire/."
#    os.system(cmd)#
#    os.chdir("md_sire")
#    md_sire(cuda_index)

def sim_cfg(crd,nmoves,ncycles,constraint,timestep,minimise):

    print("Creation of the sim.cfg files for md")
    sim_file = open("sim.cfg","w")

    sim_file.write(
'''
topfile= "solvated.parm7"
crdfile= "%s"
nmoves = %s
buffered coordinates frequency = 100
ncycles = %s
save coordinates = True
constraint = %s
timestep = %s
cutoff type = cutoffperiodic
cutoff distance = 14*angstrom
barostat = True
andersen = True
precision = mixed
center solute = True
minimise = %s
'''
    % (crd,nmoves,ncycles,constraint,timestep,minimise) )

    sim_file.close()


def md_sire(cuda_index):

    print("Running Sire to equilibate system density")
    print("Creating md_sire directory")

    if not os.path.exists("md_output"):
        os.makedirs("md_output")

    sim_cfg("md00003.rst7",1000,10,"allbonds","2*femtosecond","False")
    #TODO  add the case of running on the cluster! (for all the sander/sire/..)

    os.chdir("md_output")
    cmd = "~/sire.app/bin/somd -C ../sim.cfg -t ../solvated.parm7 -c ../md00003.rst7 -d %s -p CUDA" % cuda_index
    os.system(cmd)
    os.system("wait")

    cpptraj(tidy=True)

def cpptraj_file():

    cpptraj = open("traj.in","w")
    cpptraj.write("parm ../solvated.parm7\n")
    cpptraj.write("trajin traj*.dcd 100 100 1\n")
    cpptraj.write("trajout solvated.rst7\n")
    cpptraj.write("go\n")
    cpptraj.write("quit")
    cpptraj.close()

def cpptraj(tidy=False):

    print("Extracting the coordinates")
    print("Creatin cpptraj input file")
    cpptraj_file()
    cmd = "cpptraj -i traj.in"
    os.system(cmd)
    os.system("wait")

    print("Extract rest7 file, now I copy everything to the mother directory as SYSTEM.top and SYSTEM.crd")

    if not tidy:
        print("not tidying up")
    else:
        tidy_up()

def tidy_up():
    #tidy up everything

    cmd = "cp solvated.rst7 ../../../SYSTEM_1.crd"
    os.system(cmd)
    cmd = "cp ../solvated.parm7 ../../../SYSTEM_1.top"
    os.system(cmd)

    #cmd = "mkdir ../../../inputfiles"
    #os.system(cmd)
    #os.chdir("../../../")
    #cmd = "mv * inputfiles/."
    #os.system(cmd)

#    cmd = "mv inputfiles/SYSTEM.top . "#
#    os.system(cmd)
#    cmd = "mv inputfiles/SYSTEM.crd . "
#    os.system(cmd)
#    print("Check if you need writedistres.py")




###MAIN SCRIPT###

#mol2_file is the file we have to work with
mol2_file =sys.argv[1]
#cuda_index is the index of the GPU on the workstation I need to run Sire
#cuda_index = sys.argv[2]
#now pass to the function
parmed_add(mol2_file)#,cuda_index)
