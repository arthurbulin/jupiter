#THis script will cycle through various sims and will do everything necessary to 
#run the fmft script and create the output data files. 

#@todo Add file comprehension to this script such that i can read in the output
import numpy as np
import math
import os
import lib_merc as lme
import h5_bridge as h5b

#Assign global variables witihin the script
ind_names = lme.lib_ind_names()
#absw = lme.lib_get_absw()
absw = lme.lib_get_path('absw')
do_hdf5 = lme.lib_get_path('hdf5')
data_out = lme.lib_get_path('data_out')

def main(lookin,mode=1):
	#Lookin is simulation, mode 1: run for each half, mode 2: run for entire
	data = dict()
	for i in xrange(len(lookin)):
		print 'For ' + lookin[i]
		
		#Get folders, for HDF5 or AEI
		if do_hdf5 == 'true':
			folders = h5b.get_keys(sim=lookin[i])
			folders.sort()
			
			for j in xrange(len(folders)):
				bodies = h5b.get_keys(sim=lookin[i],set=folders[j])
				for k in bodies:
					if mode == 1:
						call_fmft(lookin[i],folders[j],k,len(bodies),1)
						call_fmft(lookin[i],folders[j],k,len(bodies),2)
					if mode == 2:
						call_fmft(lookin[i],folders[j],k,len(bodies),0)
			return 88

		else: #For NON-hdf5 support
			folders = lme.lib_get_dir(lookin[i])
			folders.sort()
		
			noaei = lme.lib_need_aei(lookin[i],folders)
			if noaei:
				lme.lib_unpack(lookin[i],noaei)
			
			#sets = dict() #Don't know what this is for. THink it was a leftover
			for j in xrange(len(folders)):
				bodies = list()
				for name in os.listdir(absw+lookin[i]+'/'+folders[j]):
					if '.aei' in name: bodies.append(name.split(".aei")[0])
				#Begin data calculations	
				for thing in bodies:
					if mode == 1:
						call_fmft(lookin[i],folders[j],thing,len(bodies),1)
						call_fmft(lookin[i],folders[j],thing,len(bodies),2)
					if mode == 2:
						call_fmft(lookin[i],folders[j],thing,len(bodies),0)

def call_fmft(sim,set,world,nfreq,mode): #where,filename,nfreq,mode):
	#Where am I hiding the source code
	sourcepath = absw + 'jupiter/fmft/'
	home_path = os.getcwd()
	
	#Tries to move to the data output area
	if os.path.isdir(data_out+sim) == False: os.mkdir(data_out+sim)
	if os.path.isdir(data_out+sim+'/'+set) == False: os.mkdir(data_out+sim+'/'+set)
	os.chdir(data_out + sim +'/'+set)

	#filename = raw_input("Your AEI File (in this directory please): ")
	if do_hdf5 =='true':
		t,a,ecc,inc,omega,capom,capm,m = h5b.retreive(sim,set,world,None,mode=1)

	else:
		t,a,ecc,inc,omega,capom,capm,m,no = np.genfromtxt(world+".aei", skip_header=4, unpack=True)
	
	#Convert from degrees to radians
	omega = omega * math.pi / 180
	capom = capom * math.pi / 180

	#Calculate longitude of pericenter and real and imaginary eccentricities
	pomega = omega + capom
	x = ecc * np.cos(pomega)
	y = ecc * np.sin(pomega)

	#Now I have to make somekind of file for the FMFT
	f = open(data_out+sim+'/'+set+'/inputfile','w')
	#There was a major mistake here. Mode 1 was running for the entire lenght and 2 was
	#running for the 2nd half length. 1 should have run for 1st half length. Nothing bad at
	#this point but I caught it before we used this data. 0 now runs full length and 1 and 2 
	#run half respectivly
	if mode == 0:
		for lin in range(len(t)):
			f.write(str(t[lin]) + ' ' + str(x[lin]) + ' ' + str(y[lin]) + '\n')
	if mode == 1:
		for lin in range(len(t)/2): 
			f.write(str(t[lin]) + ' ' + str(x[lin]) + ' ' + str(y[lin]) + '\n')
	if mode == 2:
		listrange = range(len(t)/2)
		for i in listrange:
			listrange[i] = len(t)/2 + listrange[i]
		for lin in listrange:
			f.write(str(t[lin]) + ' ' + str(x[lin]) + ' ' + str(y[lin]) + '\n')
			
	f.close()

	#Number of amplitudes to solve for
	#nfreq = raw_input('How many of the largest frequency amplitudes should we find?')

	#Output interval
	dt = t[1] - t[0]

	#Length of data in power of two apperntly?
	if mode == 0:
		power = int(math.floor(math.log(len(t),2)))
	if (mode == 2) or (mode == 1):
		power = int(math.floor(math.log(len(t)/2,2)))		
	ndata = int(2**power)

	#Read in the FMFT source code template
	mfttemplate = sourcepath + 'main_fmft_template.c'
	f = open(mfttemplate, 'r')
	lines = f.readlines()
	f.close

	#Editing template lines apparently
	lines[9] = lines[9].replace('XXX',str(int(nfreq)))
	lines[10] = lines[10].replace('YYY',str(dt))
	lines[11] = lines[11].replace('ZZZ',str(ndata))

	#Make customized FMFT source code
	mftsource = './main_fmft.c'
	f = open(mftsource,'w')
	for line in lines:
		f.write(line)
	f.close()

	#put files into interesting directory and compile
	os.system('cp ' + sourcepath + 'nrutil.h ' + sourcepath + 'nrutil.c '+ sourcepath + 'fmft.c ' + './')
	os.system('gcc -c nrutil.c')
	os.system('gcc -c fmft.c')
	os.system('gcc -o main_fmft main_fmft.c fmft.o nrutil.o -lm')
	if do_hdf5 == 'true':
		os.system('./main_fmft < inputfile > '+world+str(mode)+'.fmft')
	else:
		os.system('./main_fmft < inputfile > '+world+str(mode)+'.fmft')

	os.chdir(home_path)
