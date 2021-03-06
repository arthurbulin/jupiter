#################################################
#	Mercury Simulation setup script		#
#	Arthur Bulin arthur.a.bulin@ou.edu	#
#################################################
import os
import numpy as np
import math
import copy
import lib_merc as lme
import json
#version = "1.3.2"
#absw = lme.lib_get_absw
#sim = '39'
#skip = []

data_out = lme.lib_get_path('data_out')
absw = lme.lib_get_path('absw')
ind_names = lme.lib_ind_names()
name_values = ['name','mass','a','ecc','inc','longper','longasc','meanlong','den']
email = lme.lib_get_path('email')


###################################################
#Ecc and tpo changes for these specific cases
#Do not use this in Jupiter as it is a special case                                                        
###################################################
def main(sim,new_worlds=None,args=None,params=None,gen=10,flat_tpo=False,skip=None):
	home_dir = os.getcwd() #Commit this to memory so that the GFB script knows where to return to when done
	#Try to go to our new sim directory.
	#THis isn't strictly nesessary but I prefer to work in a directory then return home
	#In the even I need to execute a program in that directory at some point
	try: os.chdir(absw + sim)
	except OSError as er:
		ER = str(er)
		if ('errno' in str.lower(ER)) and ('2' in ER): #If a specific error print details
			print ER
			print 'Creating Directory at '+absw+sim 
			try: os.mkdir(absw+sim) #Try and create the needed directory
			except: #If that fails something is wrong with perms or your HD is likely full
				os.chdir(home_dir) #Bring Mark Watney home
				return 'Error making sim directory',str(absw+sim)
			os.chdir(absw+sim)#Directory created without exception. Go there.

	#These are now only called when args and params are fully default
	#Every time the method for defaults is called a new dict is constructed, so value is passed not association
#	if args is None:
#		args = set_default_args() #Default Args
#	if params is None:
#		params = param_defaults()
	
	#This is outdated and I will integrate it into planetary creation later
#	tp_list = ['mercury','venus','earth','mars'] #Tps
#
#	#Flatten TPOs if True
#	if flat_tpo == True:
#		for tps in tp_list:
#			args[tps]['ecc'] = .001
#			args[tps]['inc'] = .1
	#Append the new_worlds onto args
#	for i in new_worlds.keys():
#		args[i] = new_worlds[i]

	#This will generate the standard folder 0 with all files needed
	print 'Starting Generation'
#	Perform copy of base params and generate big.in files for each.             
#	if os.path.isdir('./0') == True:
	os.system('mkdir ./0')
#	print "Made Base Directory"
	gen_param(params,'./0')
#	print "Made param file"
	write_small('./0')
#	print "Made small.in"
	write_message('./0')
#	print "Made message.in"
	write_files('./0')
#	print "Made files.in"
	pl_gen(args,'./0',new_worlds=new_worlds,skip=skip)
#	print "Made big.in\n"
	
	#THis will make a copy of 0 for each sub run and then create a new big.in with same parameters but different slightly randomly
	for i in xrange(gen - 1):
		os.mkdir('./'+str(i+1))
#		print 'Made ' + str(i+1)
		os.system('cp ./0/* ./'+str(i+1))
#		print 'Copied base files to ' + str(i+1)
		pl_gen(args,'./'+str(i+1),new_worlds=new_worlds,skip=skip)
#		print 'big.in genereation complete\n'
	
	#gens the condor file
	print "Generating Condor File"
	gen_condor(sim,'.',gen)
	
	#Creates an easily reloadable JSON file with initial params and args
	print "Writing initial conditions backup JSON files."
	with open("params_"+str(sim)+".json","w") as f:
		json.dump(params,f,indent=4)
	with open("args_"+str(sim)+".json","w") as f:
		json.dump(args,f,indent=4)
	with open("worlds_"+str(sim)+".json","w") as f:
		json.dump(new_worlds,f,indent=4)
		
	print "Copying Mercury"
	os.system("cp "+absw+"jupiter/mod_mercury/mercury6_gr "+"sim"+str(sim)+"_gr")

	#Return us to starting directory(should be jupiter unless you are using gfb stand alone)
	os.chdir(home_dir) #Bring Mark Watney home
	
	return None,None
	
	
##############################################
#	These set my default arguments	     #
##############################################
#Generate the default modifies, be aware Earth's modifier is 0 for inc
def set_default_args():
	default_vals = dict()
#	arg_changes = dict()
	default_values = {'mass':1.,'a':1., 'ecc':1., 'inc':1., 'longper':1., 'longasc':1., 'meanlong':1., 'den':1.}
	planets = ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn']
	for each in planets:
		default_vals[each] = copy.deepcopy(default_values) #Don't think deepcopy is need but ill leave it
	#Earth has an inclination of 0.0, a modifyer would make no sense since 0. This allows for later modification of Earth incl
	#Without it being set to 0 always
	default_vals['earth']['inc'] = 0.0 
	return default_vals

#Fairly explanitory
def param_defaults():
 	things = {"algorithm":"hyb","start":0,"stop":1.46E+12,"interval":3.6525E+7,"timestep":2,"accuracy":"1.d-12","stop close":"no","allow collisions":"no","fragmentation":"no","express time":"years","relative time":"yes","output precision":"medium","relativity":"no","user force":"no","ejection":100,"radius":0.005,"mass":1.0,"hill":3.,"dumps":50000000,"periodic":100}
	return things

##############################################
#	Here will be the param and big.in    #
##############################################
#This is the condor file generation. Simple and straight forward.
def gen_condor(sim,where,gen):
	filename = "submission_" + sim + ".condor"
	f = open(where + "/" + filename,'w')
	f.write("Universe = vanilla\n")
	f.write("executable = sim"+sim+"_gr\n")
	f.write("log = sim"+sim+".log\n")
	f.write("output = sim"+sim+".out\n")
	f.write("error = sim"+sim+".error\n")
	if email != None:
		f.write("notification = Complete\n")
		f.write("notify_user = "+email+"\n")
	for i in xrange(gen):
		f.write("\ninitialdir = "+str(i)+"\n")
		f.write("queue\n")
	f.close()

#Imported from it's own routine
#Watch out as some values are str and some int but all must be str for writting
def gen_param(params,where):
	filename = 'param.in'
	f = open(where + "/" + filename, 'w')
	f.write(")O+_06 Integration parameters  (WARNING: Do not delete this line!!)\n")
	f.write(") Lines beginning with `)' are ignored.\n")
	f.write(")---------------------------------------------------------------------\n")
	f.write(") Important integration parameters:\n")
	f.write(")---------------------------------------------------------------------\n")
 	f.write("algorithm (MVS, BS, BS2, RADAU, HYBRID etc) = "+ params['algorithm'] + "\n")
 	f.write("start time (days)= "+ str(params['start'])+"\n")
 	f.write("stop time (days) = " + str(params['stop']) + "\n")
 	f.write("output interval (days) = "+ str(params['interval']) +"\n")
 	f.write("timestep (days) = "+ str(params['timestep']) +"\n")
 	f.write("accuracy parameter="+params['accuracy']+"\n")
	f.write(")---------------------------------------------------------------------\n")
	f.write(") Integration options:\n")
	f.write(")---------------------------------------------------------------------\n")
 	f.write("stop integration after a close encounter = "+params['stop close']+"\n")
 	f.write("allow collisions to occur = " + params['allow collisions']+"\n")
 	f.write("include collisional fragmentation = "+params['fragmentation']+"\n")
 	f.write("express time in days or years = "+params['express time']+"\n")
 	f.write("express time relative to integration start time = "+params['relative time']+"\n")
 	f.write("output precision = "+params['output precision']+"\n")
 	f.write("< not used at present >\n")
 	f.write("include relativity in integration= "+params['relativity']+"\n")
 	f.write("include user-defined force = "+params['user force']+"\n")
# 	print("include user-defined force = "+params['user force']+"\n")
	f.write(")---------------------------------------------------------------------\n")
	f.write(") These parameters do not need to be adjusted often:\n")
	f.write(")---------------------------------------------------------------------\n")
 	f.write("ejection distance (AU)= "+ str(params['ejection']) +"\n")
 	f.write("radius of central body (AU) = "+ str(params['radius']) +"\n")
 	f.write("central mass (solar) = "+ str(params['mass']) +"\n")
 	f.write("central J2 = 0\n")
 	f.write("central J4 = 0\n")
 	f.write("central J6 = 0\n")
 	f.write("< not used at present >\n")
 	f.write("< not used at present >\n")
 	f.write("Hybrid integrator changeover (Hill radii) = "+ str(params['hill']) +"\n")
 	f.write("number of timesteps between data dumps = "+ str(params['dumps']) +"\n")
 	f.write("number of timesteps between periodic effects = "+ str(params['periodic']) +"\n")
 	f.close()

#Ill add options for small bodies someday but this is pretty worthless for me right now
def write_small(where):
	filename = 'small.in'
	f = open(where + '/' + filename, 'w')
	f.write(")O+_06 Small-body initial data  (WARNING: Do not delete this line!!)\n")
	f.write(") Lines beginning with `)' are ignored.\n")
	f.write(")---------------------------------------------------------------------\n")
	f.write(" style (Cartesian, Asteroidal, Cometary) = Cart\n")
	f.write(")--------------------------------------------------------------------- \n")
	f.close()

def write_files(where):
	filename = 'files.in'
	f = open(where + '/' + filename, 'w')
	f.write(" big.in\n")
	f.write(" small.in\n")
	f.write(" param.in\n")
	f.write(" xv.out\n")
	f.write(" ce.out\n")
	f.write(" info.out\n")
	f.write(" big.dmp\n")
	f.write(" small.dmp\n")
	f.write(" param.dmp\n")
	f.write(" restart.dmp\n")
	f.close()

def write_message(where):
	filename = 'message.in'
	f = open(where + '/' + filename, 'w')
	f.write("  1  6  days \n")
	f.write("  2  6  years\n")
	f.write("  3 13  solar masses\n")
	f.write("  4  3  AU\n")
	f.write("  5  3 no \n")
	f.write("  6  3 yes\n")
	f.write("  7  3 low\n")
	f.write("  8  6 medium\n")
	f.write("  9  4 high\n")
	f.write(" 10  0 \n")
	f.write(" 11 33            Integration parameters\n")
	f.write(" 12 33            ----------------------\n")
	f.write(" 13 14    Algorithm:\n")
	f.write(" 14 38 Second-order mixed-variable symplectic\n")
	f.write(" 15 24 Bulirsch-Stoer (general)\n")
	f.write(" 16 37 Bulirsch-Stoer (conservative systems)\n")
	f.write(" 17 16 15th-order RADAU\n")
	f.write(" 18  0 \n")
	f.write(" 19  0\n")
	f.write(" 20  0 \n")
	f.write(" 21  0 \n")
	f.write(" 22  5 Test\n")
	f.write(" 23 48 Hybrid symplectic integrator (mixed coordinates)\n")
	f.write(" 24 44 Hybrid symplectic (close binary coordinates)\n")
	f.write(" 25 43 Hybrid symplectic (wide binary coordinates)\n")
	f.write(" 26 32    Integration start epoch:\n")
	f.write(" 27 32    Integration stop  epoch:\n")
	f.write(" 28 32    Output interval:\n")
	f.write(" 29 32    Element origin:\n")
	f.write(" 30 31    Initial timestep:\n")
	f.write(" 31 36    Accuracy parameter:\n")
	f.write(" 32 36    Central mass:\n")
	f.write(" 33 36    J_2:\n")
	f.write(" 34 36    J_4:\n")
	f.write(" 35 36    J_6:\n")
	f.write(" 36 36    Ejection distance:\n")
	f.write(" 37 36    Radius of central body:\n")
	f.write(" 38 29    Number of Big bodies:\n")
	f.write(" 39 29    Number of Small bodies:\n")
	f.write(" 40 37    Output precision: \n")
	f.write(" 41 40    Includes collisions:\n")
	f.write(" 42 40    Includes fragmentation: \n")
	f.write(" 43  0 \n")
	f.write(" 44  0 \n")
	f.write(" 45 40    Includes relativity: \n")
	f.write(" 46 40    Includes user-defined force routine: \n")
	f.write(" 47 10 barycentre \n")
	f.write(" 48 12 central body\n")
	f.write(" 49  0 \n")
	f.write(" 50  0 \n")
	f.write(" 51 30            Integration details\n")
	f.write(" 52 30            -------------------\n")
	f.write(" 53 29    Initial energy:\n")
	f.write(" 54 29    Initial angular momentum:\n")
	f.write(" 55 65    Integrating massive bodies and particles up to the same epoch.\n")
	f.write(" 56 34    Beginning the main integration.\n")
	f.write(" 57 24    Integration complete.\n")
	f.write(" 58 48    Fractional energy change due to integrator: \n")
	f.write(" 59 48    Fractional angular momentum change:\n")
	f.write(" 60 57    Fractional energy change due to collisions/ejections: \n")
	f.write(" 61 57    Fractional angular momentum change:\n")
	f.write(" 62 47    Continuing integration from dump files at \n")
	f.write(" 63  6 Time: \n")
	f.write(" 64  6 Date: \n")
	f.write(" 65  9    dE/E: \n")
	f.write(" 66  9    dL/L: \n")
	f.write(" 67 35  collided with the central body at \n")
	f.write(" 68 12  ejected at \n")
	f.write(" 69 12  was hit by \n")
	f.write(" 70 34  removed due to an encounter with \n")
	f.write(" 71  4  at \n")
	f.write(" 72 26  solar masses AU^2 day^-2\n")
	f.write(" 73 26  solar masses AU^2 day^-1\n")
	f.write(" 74 36  lost mass due to rotational breakup\n")
	f.write(" 75 24  removed due to small a\n")
	f.write(" 76  0 \n")
	f.write(" 77  0 \n")
	f.write(" 78  0 \n")
	f.write(" 79  0 \n")
	f.write(" 80  0 \n")
	f.write(" 81  8  ERROR:\n")
	f.write(" 82 49        Modify mercury.inc and recompile Mercury.\n")
	f.write(" 83 62        Check the file containing initial data for Big bodies.\n")
	f.write(" 84 64        Check the file containing initial data for Small bodies.\n")
	f.write(" 85 57        Check the file containing integration parameters.\n")
	f.write(" 86 22        Check files.in\n")
	f.write(" 87 27 This file already exists:  \n")
	f.write(" 88 34 This file is needed to continue:  \n")
	f.write(" 89 30 This filename is duplicated: \n")
	f.write(" 90 40 The total number of bodies exceeds NMAX.\n")
	f.write(" 91 68 Data style on first line must be Cartesian, Asteroidal or Cometary\n")
	f.write(" 92 68 You cannot integrate non-gravitational forces using this algorithm.\n")
	f.write(" 93 64 You cannot integrate a user-defined force using this algorithm.\n")
	f.write(" 94 64 You cannot integrate massive Small bodies using this algorithm.\n")
	f.write(" 95 66 Massive Small bodies must have the same epoch as the Big bodies.\n")
	f.write(" 96 49 Check character implies input file is corrupted.\n")
	f.write(" 97 62 Mass, density, encounter limit must be >= 0 for this object:\n")
	f.write(" 98 46 This integration algorithm is not available: \n")
	f.write(" 99 50 A problem occurred reading the parameter on line\n")
	f.write("100 50 A problem occurred reading data for this object: \n")
	f.write("101 56 A problem occured reading the epoch for the Big bodies.\n")
	f.write("102 67 You cannot use non-zero J2,J4,J6 using the close-binary algorithm.\n")
	f.write("103 34 Two objects both have this name: \n")
	f.write("104 36         is corrupted at line number: \n")
	f.write("105 42 Central-body radius exceeds maximum radius. \n")
	f.write("106 68 Maximum/Central radius is large. Output precision will be degraded. \n")
	f.write("107 58 Coordinate origin must be Central, Barycentric or Jacobi.\n")
	f.write("108  0 \n")
	f.write("109  0 \n")
	f.write("110  0 \n")
	f.write("111  0 \n")
	f.write("112  0 \n")
	f.write("113  0 \n")
	f.write("114  0 \n")
	f.write("115  0 \n")
	f.write("116  0 \n")
	f.write("117  0 \n")
	f.write("118  0 \n")
	f.write("119  0 \n")
	f.write("120  0 \n")
	f.write("121 10  WARNING:\n")
	f.write("122 53 Truncating the name of this object to 8 characters: \n")
	f.write("123 30 Main integration is backwards.\n")
	f.write("124 26 No Big bodies are present.\n")
	f.write("125 28 No Small bodies are present.\n")
	f.write("126 50 Stopping integration due to an encounter between \n")
	f.write("127 45 Throwing this object into the central body: \n")
	f.write("128 42 Setting output threshhold DA to infinity.\n")
	f.write("129 42 Setting output threshhold DE to infinity.\n")
	f.write("130 42 Setting output threshhold DI to infinity.\n")
	f.write("131 43 Increasing the radius of the central body.\n")
	f.write("132 56 Total number of current close encounters exceeds CMAX.\n")
	f.write("133  0 \n")
	f.write("134  0 \n")
	f.write("135  0 \n")
	f.write("136  0 \n")
	f.write("137  0 \n")
	f.write("138  0 \n")
	f.write("139  0 \n")
	f.write("140  0 \n")
	f.write("141  0 \n")
	f.write("142  0 \n")
	f.write("143  0 \n")
	f.write("144  0 \n")
	f.write("145  0 \n")
	f.write("146  0 \n")
	f.write("147  0 \n")
	f.write("148  0 \n")
	f.write("149  0 \n")
	f.write("150  0 \n")
	f.write("151 67 )O+_05 Integration parameters  (WARNING: Do not delete this line!!)\n")
	f.write("152 66 )O+_05 Big-body initial data  (WARNING: Do not delete this line!!)\n")
	f.write("153 68 )O+_05 Small-body initial data  (WARNING: Do not delete this line!!)\n")
	f.write("154 39 ) Lines beginning with `)' are ignored.\n")
	f.write("155 70 )---------------------------------------------------------------------\n")
	f.write("156 43  style (Cartesian, Asteroidal, Cometary) = \n")
	f.write("157 20  epoch (in days) = \n")
	f.write("158 35 ) Important integration parameters:\n")
	f.write("159 48  algorithm (MVS, BS, BS2, RADAU, HYBRID etc) = \n")
	f.write("160 21  start time (days) = \n")
	f.write("161 20  stop time (days) = \n")
	f.write("162 26  output interval (days) = \n")
	f.write("163 19  timestep (days) = \n")
	f.write("164 22  accuracy parameter = \n")
	f.write("165 22 ) Integration options:\n")
	f.write("166 44  stop integration after a close encounter = \n")
	f.write("167 29  allow collisions to occur = \n")
	f.write("168 37  include collisional fragmentation = \n")
	f.write("169 33  express time in days or years = \n")
	f.write("170 51  express time relative to integration start time = \n")
	f.write("171 20  output precision = \n")
	f.write("172 24  < Not used at present > \n")
	f.write("173 37  include relativity in integration = \n")
	f.write("174 30  include user-defined force = \n")
	f.write("175 52 ) These parameters do not need to be adjusted often:\n")
	f.write("176 26  ejection distance (AU) = \n")
	f.write("177 31  radius of central body (AU) = \n")
	f.write("178 31  central mass (solar masses) = \n")
	f.write("179 14  central J2 = \n")
	f.write("180 14  central J4 = \n")
	f.write("181 14  central J6 = \n")
	f.write("182 24  < Not used at present > \n")
	f.write("183 24  < Not used at present > \n")
	f.write("184 45  Hybrid integrator changeover (Hill radii) = \n")
	f.write("185 42  number of timesteps between data dumps = \n")
	f.write("186 48  number of timesteps between periodic effects = \n")
	f.write("187 41  origin (Central, Barycentric, Jacobi) = \n")
	f.write("188  0 \n")
	f.write("189  0 \n")
	f.write("190  0 \n")
	f.write("191  0 \n")
	f.write("192  0 \n")
	f.write("193  0 \n")
	f.write("194  0 \n")
	f.write("195  0 \n")
	f.write("196  0 \n")
	f.write("197  0 \n")
	f.write("198  0 \n")
	f.write("199  0 \n")
	f.write("200  0 \n")
	f.close()


#Originaly from Nate Kaib. Modified for use with Jupiter by Arthur Bulin
#Feburary 12 2016
#Modified again. 
#WARNING. This routine needs a rewrite for the mass work. I accounted for weird mass notation with a fix in one of the
#later methods. However, my fix didn't account for uppercase vs. lowercase. This gave freaky masses for the jovians.
#I fixed this to UPPER or lower case will work, but not a mix of both. I will make sure that all user input is cast lowercase.
#But for now beware 6/17/16

def anomcalc(meananom,ecc):
    """calculates eccentric anomaly from the mean anomaly"""
    #based on Murray and Dermot
    meananom=np.asarray(meananom)
    ecc=np.asarray(ecc)
    k=0.85
    sign=np.sin(meananom)/np.fabs(np.sin(meananom))

    E0=meananom+sign*k*ecc
    E=E0

    sel=np.arange(0,len(E0))
    fracdiff=sel*0.+1.
    sel2=np.where(ecc >= 1)
    fracdiff[sel2]=0.

    while np.amax(fracdiff) > 0.001:
        f0=E[sel]-ecc[sel]*np.sin(E[sel])-meananom[sel]
        f1=1.-ecc[sel]*np.cos(E[sel])
        f2=ecc[sel]*np.sin(E[sel])
        f3=ecc[sel]*np.cos(E[sel])
        
        del1=-f0/f1
        del2=-f0/(f1+.5*del1*f2)
        del3=-f0/(f1+.5*del2*f2+1./6.*del2**2*f3)

        nextone=E[sel]+del3
        diff=E[sel]-nextone
        fracdiff[sel]=np.fabs(diff/E[sel])
        
        E[sel]=nextone
        sel=np.where((fracdiff > 0.001))

        sel2=np.where(ecc >= 1)
        fracdiff[sel2]=0.

    sel2=np.where(ecc >= 1)
    E[sel2]=2.*math.pi*1.0001
#    print 'ecc anom'
#    print E
    return(E)



def angcalc(E,ecc):
    """calculates the true anomaly from the eccentric anomaly"""
    E=np.asarray(E)
    ecc=np.asarray(ecc)

    cosang=(np.cos(E)-ecc)/(1-ecc*np.cos(E))
    angpos=np.arccos(cosang)

    #sometimes E is just under 0...this is wrong    
    E=np.fabs(E)

    #output of arccos goes from 0 to pi, but real angles go up to 2*pi
    #we need to correct for this
    acoscorrec=np.floor(E/math.pi)*2*math.pi

    #however sometime E is just over 2*pi.  these don't need corrected
    Enoisecorrec=np.floor(E/(2*math.pi))*4.*math.pi
    acoscorrec=acoscorrec-Enoisecorrec

    #correcting angpos
    angpos=acoscorrec-angpos
    angpos=(angpos*angpos)**.5

    return(angpos)


def rcalc(E,a,ecc):
    """calculates distance from Sun for a given orbit and ecc. anomaly"""
    r=a*(1.-ecc*np.cos(E))

    return(r)



def pl_gen(arg_changes,dir,new_worlds=None,skip=None):
    """generates a tp initial conditions file for SCATR"""
    #if arg_changes == None:
    #	arg_changes = set_default_args()
    	
#    names,denlist,mass,a,ecc,inc,longper,longasc,meanlong = planet_create()
   # ['name','mass','a','ecc','inc','longper','longasc','meanlong','den']
    names,mass,a,ecc,inc,longper,longasc,meanlong,denlist = create_planets(arg_changes,new_worlds=new_worlds)
    planetnum = len(names) + 1
#    names = ['JUPITER','SATURN','MERCURY','VENUS','EARTH','MARS']
#    denlist = [1.,1.,3.,3.,3.,3.]
#    mass=np.empty(planetnum)
    Msun = mass[0]*1.0
    #Msun=2.959139768995959e-04
    #mass[0]=Msun*1.0
#    a=np.empty(planetnum-1)
#    ecc=np.empty(planetnum-1)
#    inc=np.empty(planetnum-1)
#    longper=np.empty(planetnum-1)
#    longasc=np.empty(planetnum-1)
#    meanlong=np.empty(planetnum-1)
    
    inc=inc*math.pi/180.
    longper=longper*math.pi/180.
    longasc=longasc*math.pi/180.
    meanlong=meanlong*math.pi/180.
    meananom=meanlong-longper #see p. 34 of Murray and Dermott

    #transforming random mean anomalies into actual orbital positions
    eccanom=anomcalc(meananom,ecc)
    angpos=angcalc(eccanom,ecc)
    rpos=rcalc(eccanom,a,ecc)
    argper=longper-longasc #see p. 49 of Murray and Dermott
	#Converting the orbitalelements into actual xyz data 164-201
    #transform into actual positions and velocities
    transformx = (np.cos(longasc) * np.cos(argper + angpos) - np.sin(longasc) * np.sin(argper + angpos) * np.cos(inc))
    transformy = (np.sin(longasc) * np.cos(argper + angpos) + np.cos(longasc) * np.sin(argper + angpos) * np.cos(inc))
    transformz = np.sin(argper + angpos) * np.sin(inc)
#    print 'transforms ' + str(transformx) + ' ' + str(transformy) + ' ' + str(transformz)
    #transforming coords
    gencoordx = np.empty(planetnum)*0.0
    gencoordy = np.empty(planetnum)*0.0
    gencoordz = np.empty(planetnum)*0.0
    gencoordx[1:planetnum] = rpos * transformx
    gencoordy[1:planetnum] = rpos * transformy 
    gencoordz[1:planetnum] = rpos * transformz

    #calculating velocities in specific orbit coordinate
# I am unsure of this next line. This is Nate's code so I am not sure if i am not understanding it.
# I have commented it out because it causes a singularity. But signinc is never called anyway.
# This is the only occurance.
#    signinc = inc / np.fabs(inc)
    period = np.sqrt(4 * math.pi**2 * a**3 / mass[0])
    angvel = 2 * math.pi / period

    #doing velocity transformations...see p. 31 and 51 of Murray and Dermott
    xdot = -angvel * a * np.sin(angpos) / np.sqrt(1 - ecc**2)
    ydot = angvel * a * (ecc + np.cos(angpos)) / np.sqrt(1 - ecc**2)
    zdot = 0 * angpos

    genvelx = np.empty(planetnum)*0.0
    genvely = np.empty(planetnum)*0.0
    genvelz = np.empty(planetnum)*0.0
    genvelx[1:planetnum] = ((np.cos(argper) * np.cos(longasc) - np.sin(argper) *
            np.sin(longasc) * np.cos(inc)) * xdot - (np.sin(argper) *
            np.cos(longasc) + np.cos(argper) * np.sin(longasc) *
            np.cos(inc)) * ydot)
    genvely[1:planetnum] = ((np.cos(argper) * np.sin(longasc) + np.sin(argper) *
            np.cos(longasc) * np.cos(inc)) * xdot + (np.cos(argper) *
            np.cos(longasc) * np.cos(inc) - np.sin(argper) *
            np.sin(longasc)) * ydot)
    genvelz[1:planetnum] = ((np.sin(argper) * np.sin(inc)) * xdot +
            (np.cos(argper) * np.sin(inc)) * ydot)
	#end conversion 164-201
	#start orientation to invarient plane set my system's angmom 204-247
    Lx = np.sum((gencoordy*genvelz - gencoordz*genvely) * mass)
    Ly = np.sum((gencoordz*genvelx - gencoordx*genvelz) * mass)
    Lz = np.sum((gencoordx*genvely - gencoordy*genvelx) * mass)
    Ltot = np.sqrt(Lx*Lx + Ly*Ly + Lz*Lz)
    Lxhat = Lx/Ltot
    Lyhat = Ly/Ltot
    Lzhat = Lz/Ltot

    thet = np.arctan2(Lyhat,Lxhat)
    phi = np.arcsin(Lzhat)

    #rotate around z-axis so all ang. momentum is in x-z plane
    thet = -thet
    for i in range(planetnum):
        rotz=[[np.cos(thet),-np.sin(thet),0],[np.sin(thet),np.cos(thet),0],[0,0,1]]
        pos = [[gencoordx[i]],[gencoordy[i]],[gencoordz[i]]]
        vel = [[genvelx[i]],[genvely[i]],[genvelz[i]]]

        pos = np.dot(rotz, pos)
        vel = np.dot(rotz, vel)

        gencoordx[i] = pos[0]
        gencoordy[i] = pos[1]
        gencoordz[i] = pos[2]
        genvelx[i] = vel[0]
        genvely[i] = vel[1]
        genvelz[i] = vel[2]

    #rotating around y-axis to align all ang. momentum with z-axis
    phi = -(math.pi/2. - phi)
    for i in range(planetnum):
        roty=[[np.cos(phi),0,np.sin(phi)],[0,1,0],[-np.sin(phi),0,np.cos(phi)]]
        pos = [[gencoordx[i]],[gencoordy[i]],[gencoordz[i]]]
        vel = [[genvelx[i]],[genvely[i]],[genvelz[i]]]

        pos = np.dot(roty, pos)
        vel = np.dot(roty, vel)

        gencoordx[i] = pos[0]
        gencoordy[i] = pos[1]
        gencoordz[i] = pos[2]
        genvelx[i] = vel[0]
        genvely[i] = vel[1]
        genvelz[i] = vel[2] #end orientation 

    #create tp.in file
    filename= '/big.in'
    f = open(dir + filename, 'w')
    f.write(')O+_06 Big-body initial data  (WARNING: Do not delete this line!!)\n')
    f.write(') Lines beginning with ) are ignored.\n')
    f.write(')---------------------------------------------------------------------\n')
    f.write(' style (Cartesian, Asteroidal, Cometary) = Cartesian\n')
    f.write(' epoch (in days) = 0.0\n')
    f.write(')---------------------------------------------------------------------\n')


    #select masses and radii
#    print names
 #   print mass
  #  print mass/Msun
    for j in range(1,planetnum):
#    	print range(1,planetnum)
	if skip != None:
		if names[j-1] in skip:
			continue
        mass[j] = mass[j]/Msun
#        massing = mass[j]*1.98855e33
        density = denlist[j-1]
        f.write(names[j-1] + ' m='+str(mass[j])+' r=1.D0 d='+str(density)+'\n')
        
        randthet = np.random.random_sample(1)*math.pi*2.
        randcosphi = np.random.random_sample(1)*2.-1.
        randphi = math.acos(randcosphi)
        randx = 1e-9*math.cos(randthet)*math.cos(randphi)
        randy = 1e-9*math.sin(randthet)*math.cos(randphi)
        randz = 1e-9*math.sin(randphi)

        newx,newy,newz = gencoordx[j]+randx, gencoordy[j]+randy, gencoordz[j]+randz
        f.write('  '+'%.15e' % newx +' '+'%.15e' % newy +' '+'%.15e' % newz +'\n')
        f.write(str(genvelx[j]) + ' ' + str(genvely[j]) + ' ' + str(genvelz[j])+'\n')
        f.write('0. 0. 0.\n')

    f.close()

def create_planets(arg_changes,new_worlds=None,m_sun=2.959139768995959e-04):
	"""Generates defaults for the standard worlds"""
	#Put in possible exception warning
	if arg_changes == None and new_worlds == None:
		print "NO input!"
		print "Anything this spits out with probably fail. Check NewWorlds and arg_changes."

	#Skip was removed from here. with the defaults and a skip list we can yank them out in pl_gen
	if arg_changes != None:
		defaults = dict()
		#load default values
		names = np.genfromtxt(absw+'jupiter/orbital_defaults.cfg',skip_header=1,dtype=str,usecols=0)
		bork,mass,a,ecc,inc,longper,longasc,meanlong,den = np.genfromtxt(absw+'jupiter/orbital_defaults.cfg',unpack=True,skip_header=1)
#		print "Names"
#		print names
#		print "MAss"
#		print mass
#		print "Mass / sun"
#		print mass *  m_sun

		#bork is a trash array. Its a meme joke but its easier to pull in the array and trash it then do the annoying code to skip first colum and get all others
	#???	names = np.array([str.lower(i) for i in names])
		#Lowercase skip for comparison
	#	if skip != None: skip = [str.lower(i) for i in skip]
#		print "685"
		names = [str.lower(i) for i in names]
		arg_keys = [str(i) for i in arg_changes.keys()]
#		print arg_keys
#		print names
		#Commit these things to dict
		for i in xrange(len(names)):
#			if (names[i] not in arg_keys) and (str.upper(names[i]) not in arg_keys): #This allows us to do a reduced solar system with out key error
#				print "690"
#				print names[i]
#				continue
#			else:	
#				print "694-1"
			temp_dict = dict()
#				print "694"
#			print "loop"
#			print names[i]
#			print mass[i]
			temp_dict['mass'] = mass[i] * arg_changes[names[i]]['mass']
			temp_dict['a'] = a[i] * arg_changes[names[i]]['a']
			temp_dict['ecc'] = ecc[i] * arg_changes[names[i]]['ecc']
			temp_dict['inc'] = inc[i] * arg_changes[names[i]]['inc']
			temp_dict['longper'] = longper[i] * arg_changes[names[i]]['longper']
			temp_dict['longasc'] = longasc[i] * arg_changes[names[i]]['longasc']
			temp_dict['meanlong'] = meanlong[i] * arg_changes[names[i]]['meanlong']
			temp_dict['den'] = den[i] * arg_changes[names[i]]['den']
#			print "703"
			defaults[names[i]] = temp_dict		
	
	
		core_list = list()
#changing the way skip works because it sucks
#		if skip != None:
	#		print "skip loop"
#			key_l = [str(i) for i in defaults.keys()]
#			for i in xrange(len(skip)):
	#			print "iter" + str(skip[i])
#				print skip
#				print defaults.keys()
	#			print key_l
#	#			print i
#				if skip[i] in key_l:
	#				print "i1"
#					defaults.pop(skip[i], None)
					#del defaults[skip[i]]
	#				print defaults
#				elif str.swapcase(skip[i]) in key_l:
	#				print "i2"
#					defaults.pop(str.swapcase(skip[i], None))
#					del defaults[str.upper(skip[i])]
#				elif str.lower(skip[i]) in key_l:
#					print "i3"
#					del defaults[str.lower(skip[i])]
					
		#Assemble the lists for default worlds
	#	print "for loop"
		for i in names:
	#		if i in skip: continue
#			if i not in arg_keys: #This allows us to do a reduced solar system
#				continue
			tmp_list = list()
			tmp_list.append(i)
			for j in name_values[1:]:
	#			if j in skip: continue
				tmp_list.append(defaults[i][j])
			core_list.append(tmp_list)
	
	elif arg_changes == None:
		core_list = list()
	#Append custom worlds to default worlds
	#Doing this could probably be done more efficiently but I will adress that later.
	#This deals with allowing me to do the default worlds IN ORDER in the default file
	#print "For 2"
	if new_worlds != None:
		new_worlds_keys = [str(i) for i in new_worlds.keys()]
		for i in new_worlds.keys():
			tmp_list = list()
			tmp_list.append(i)
			for j in name_values[1:]:
				tmp_list.append(new_worlds[i][j])
			core_list.append(tmp_list)
#	print core_list
#	print "err?"
	core_array = np.flipud(np.rot90(np.asarray(core_list)))
	mass_array = np.empty(len(core_array[1])+1)
	mass_array[0] = m_sun
#	tmp_arr = np.array(len(core_array[1]))
#	for j in xrange(len(core_array[1])):
#		tmp_arr[j] = core_array[1][j] * m_sun
	mass_array[1:] = np.float64(core_array[1]) * m_sun
#	print "Core Mass"
#	print core_array[1]
#	print "Mass Array!!!"
#	print mass_array
#Test comment out these	
#	print core_array
	#Corrects for odd mass notation
#	if skip != None:
#		tmp_l = list()
#		for i in xrange(len(arg_keys)):
#			if arg_keys[i] not in skip:
##				tmp_l.append(arg_keys[i])
#		arg_keys = tmp_l
		
	if arg_changes != None:
		arg_keys = np.asarray(core_array[0]) 
		#This resets arg_keys. There is a problem using arg keys like this
		#it messes with the order and the mass gets out of order
#		print mass_array
		for i in xrange(len(arg_keys)):
			if ('JUPITER' == arg_keys[i]) or ('SATURN' == arg_keys[i]):
#				print arg_keys[i]
				mass_array[1+i] = mass_array[1+i] / m_sun
#				print mass_array[1+i]
			elif ('jupiter' == arg_keys[i]) or ('saturn' == arg_keys[i]):
#				print arg_keys[i]
				mass_array[1+i] = mass_array[1+i] / m_sun
#				print mass_array[1+i]

			
#	return core_list
#	core_array[2:] = np.float64(core_array[2:])
#	print "Mass Array"
#	print mass_array
#	print "Names"
#	print core_array[0]
		
	return core_array[0],mass_array,np.float64(core_array[2]),np.float64(core_array[3]),np.float64(core_array[4]),np.float64(core_array[5]),np.float64(core_array[6]),np.float64(core_array[7]),np.float64(core_array[8])
	

def create_new_worlds():
	new_worlds = dict() #holds the new worlds and worlds from file
	file_writes = list()  #Holds name of loaded worlds to prevent conflicts
	world_values = ['Name','Mass','Semimajor Axis','Eccentricity','Inclination','Longitude of Pericenter','Longitude of Ascending Node','Mean Anomaly','Density']
#	name_values = ['name','mass','a','ecc','inc','longper','longasc','meanlong','den']
	constraints = {'a': "In AU",
			'den': '',
			'ecc': '',
			'inc': '',
			'longasc':'',
			'longper':'',
			'mass': 'In solar masses',
			'meanlong':''}
	while True:
		print "\tWorld Creation Menu"
#		print "If you use custom worlds a record will be created for your worlds when you exit with (2)"
#		print "Exiting with (3) will discard worlds"
#		print "Option (4) will generate the records file manualy\n"
		
		print "1: Create a new world"
		print "2: Return to simulation setup with Worlds"
		print "3: Return to setup WITHOUT Worlds"
		print "4: Write world record and exit to menu"
		print "5: Load worlds record"
		print "0: Exit JUPITER"
		
		while True:
			input_v = input('>')
			if input_v == 0:
				return 0,None
				
			elif input_v == 1: #create new world
				temp_holder = dict() #Temp holder data
				print "World Creation. Please follow the prompts."
				print "Hit return with no entry to exit at any time"
				
				if len(new_worlds) > 0: #If they exist print worlds
					print "Existing Custom worlds: ",
					for i in new_worlds:
						print i,
					print '\n'
				
				print "New world: " #Start new world
				for i in xrange(len(world_values)): #Start commit loop for new world data
					while True:
						value = raw_input(world_values[i]+'>') #Collect user input
						if value == '': break #If user hits return with no value then break loop
						elif name_values[i] == 'name': #If entering name data check it is acceptible
							if len(value) > 8: #Check of length. If too long, fix it.
								value = value[0:7]
								print "That name is to long. Truncating to 8 characters."
							if value in new_worlds: #Check existance
								print "That name already exists."
								#break #If it does make them try again
							else:
								name_temp = value #Assign the name
								break
						else: #If it isnt '' or name add it to the values
							try: 
								temp_holder[name_values[i]] = np.float64(value)
								break
							except: 
								print "Bad value. That cannot be cast as a float"
					if value == '':
						print "Returning to main menu"
						break
				if value != '':
					new_worlds[name_temp] = temp_holder #Commit it to the dictionary for the worlds
				input_v = 90

			elif input_v == 2: #return to sim setup
				if len(new_worlds) == 0:
					print "Returning with no custom worlds."
					return 77,None
				else: #If returning with worlds
					if os.path.isfile(data_out+'custom_worlds.json'): #If custom worlds record exists
						with open(data_out+'custom_worlds.json') as custom_worlds:
							custom_load = json.load(custom_worlds)
						
						#Create list of conflicts
						conflicts_raw = list()
						conflicts = list()
						for i in new_worlds.keys():
							if unicode(i) in custom_load.keys():
								conflicts_raw.append(i)
						#Establish if conflicts and loads are same
						for i in conflicts_raw:
							if i not in file_writes:
								conflicts.append(i)
						
						if len(conflicts) > 0: #Conflicts found
							print "Conflict found in writting record of custom worlds"
							print "1: Resolve conflicts and write record"
							print "2: Do not write record and continue with custom worlds"
							print "3: Discard worlds and return to JUPITER menu"
							input_v = input('>')
							
							if input_v == 0: #Force exit JUPITER
								return 0,None
							elif input_v == 1: #Resolve Conflicts
								state,new_worlds = custom_duality(new_worlds,custom_load)
							elif input_v == 2: #Ignore conflicts, no record
								return 88,new_worlds
							elif input_v == 3: #Discard all and go home
								return 77,None
						else: #No conflicts found
							#append and write file
							for i in new_worlds.keys():
								custom_load[i] = new_worlds[i]
							with open(data_out+'custom_worlds.json','w') as custom_worlds:
								json.dump(custom_load,custom_worlds,indent=4)
							return 88,new_worlds
					else:
					#Write file here
						#f = open(data_out+'custom_worlds.json','w')
						with open(data_out+'custom_worlds.json','w') as custom_worlds:
							json.dump(new_worlds,custom_worlds,indent=4)
						#f.close(),
						return 88,new_worlds
			
			elif input_v == 3: #Return to setup w/o worlds
				return 77,None
				
			elif input_v == 4: #Write record
				with open(data_out+'custom_worlds.json') as custom_worlds:
					json.dump(new_worlds,custom_worlds,indent=4)
					
			elif input_v == 5: #Load worlds from record
				print "Load worlds from record"
			else:
				print "This is not a valid option"
			if input_v == 90: break #Use this to break loops and reprint main menu
			
def create_mhr_planets(ainner,npl,mpl,nhill):
	'''Generates a new_worlds dict for planetary assembly with worlds seperated by Mutual hill radi'''
	#MPL should be a list or np array
	Msun = 2.959139768995959e-04
	Mearth = Msun * 3e-06
#	massivenum = npl + 1 #Includes the sun
	
	worlds = dict()
	
	names = list()
	for i in xrange(npl):
		names.append('PL'+str(i))
	
	#denlist = np.ones(npl)
	mass = np.empty(npl+1)
	mass[0] = Msun
	mass[1:] = np.asarray(mpl) * Mearth
	a = np.empty(npl)
	#ecc = np.empty(npl)
	#inc = np.empty(npl)
	#longper = np.empty(npl)
	#longasc = np.empty(npl)
	#meanlong = np.empty(npl)
	
	for i in xrange(npl):
		if i == 0:
			a[i] = ainner
		else:
			mfactor = ((mass[i+1] + mass[i]) / (3. * Msun))**(1./3.)
			a[i] = a[i-1] * (1. + nhill/2. * mfactor) / (1. - nhill/2. * mfactor)
		
		tmp_d = dict()
		tmp_d['a'] = a[i]
		tmp_d['ecc'] = 1e-2 * np.random.random_sample(1)[0]
		tmp_d['inc'] = 1. * np.random.random_sample(1)[0]
		for j in ['longper','longasc','meanlong']:
			tmp_d[j] = 360. * np.random.random_sample(1)[0]
		tmp_d['den'] = 1.
		tmp_d['mass'] = mass[i+1] / Msun

		worlds[names[i]] = tmp_d
	
	return worlds

#def generate_string(masses,space,start)	
	
				
#def format_planetary_data(worlds,m_sun=2.959139768995959e-04):
#	world_values = ['Name','Mass','Semimajor Axis','Eccentricity','Inclination','Longitude of Pericenter','Longitude of Ascending Node','Mean Anomaly','Density']

				
#Conflict resolution				
#def custom_duality(conflicts,worlds,loads):
#	print "




    #Here is where he selects orbital elements for the planets?    
    #MERCURY
#    mass[3]=1.660e-7*Msun * arg_changes['mercury']['mass']
#    a[2]=0.3871 * arg_changes['mercury']['a']
#    ecc[2]=0.2056 * arg_changes['mercury']['ecc']
#    inc[2]=7.0049 * arg_changes['mercury']['inc']
#    longper[2]=77.456 * arg_changes['mercury']['longper']
#    longasc[2]=48.3317 * arg_changes['mercury']['longasc']
#    meanlong[2]=252.251 * arg_changes['mercury']['meanlong']

    #VENUS0
#    mass[4]=2.447e-6*Msun * arg_changes['venus']['mass']
#    a[3]=0.7233 * arg_changes['venus']['a']
#    ecc[3]=0.00677 * arg_changes['venus']['ecc']
#    inc[3]=3.3947 * arg_changes['venus']['inc']
#    longper[3]=131.53298 * arg_changes['venus']['longper']
#    longasc[3]=76.6807 * arg_changes['venus']['longasc']
#    meanlong[3]=181.9797 * arg_changes['venus']['meanlong']
    
#    #EARTH
#    mass[5]=3.002e-6*Msun * arg_changes['earth']['mass']
#    a[4]=1.0 * arg_changes['earth']['a']
#    ecc[4]=0.0167 * arg_changes['earth']['ecc']
#    inc[4]=arg_changes['earth']['inc']
#    longper[4]=102.95 * arg_changes['earth']['longper']
#    longasc[4]=348.74 * arg_changes['earth']['longasc']
#    meanlong[4]=100.46 * arg_changes['earth']['meanlong']

    #MARS
#    mass[6]=3.226e-7*Msun * arg_changes['mars']['mass']
#    a[5]=1.5237 * arg_changes['mars']['a']
#    ecc[5]=0.0934 * arg_changes['mars']['ecc']
#    inc[5]=1.8506 * arg_changes['mars']['inc']
#    longper[5]=336.04 * arg_changes['mars']['longper']
#    longasc[5]=49.579 * arg_changes['mars']['longasc']
#    meanlong[5]=355.4533 * arg_changes['mars']['meanlong']

    #Saturn
#    mass[2]=8.450771312702512e-08 * arg_changes['saturn']['mass']
#    a[1]=9.537 * arg_changes['saturn']['a']
#    ecc[1]=.05415 * arg_changes['saturn']['ecc']
#    inc[1]=2.48466 * arg_changes['saturn']['inc']
#    longper[1]=92.43 * arg_changes['saturn']['longper']
#    longasc[1]=113.7 * arg_changes['saturn']['longasc']
#    meanlong[1]=49.9 * arg_changes['saturn']['meanlong']
    
    #Jupiter
#    mass[1]=2.825328644877726e-07 * arg_changes['jupiter']['mass']
#    a[0]=5.203 * arg_changes['jupiter']['a']
#    ecc[0]=0.0488 * arg_changes['jupiter']['ecc']
#    inc[0]=1.305 * arg_changes['jupiter']['inc']
#    longper[0]=14.754 * arg_changes['jupiter']['longper']
#    longasc[0]=100.556 * arg_changes['jupiter']['longasc']
#    meanlong[0]=34.404 * arg_changes['jupiter']['meanlong']
