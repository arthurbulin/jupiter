#THis script will cycle through various sims and will do everything necessary to 
#run the fmft script and create the output data files. 

#@todo Add file comprehension to this script such that i can read in the output
import numpy as np
import math
import os

ind_names = range(10)
for i in ind_names:
	ind_names[i] = str(i)
	
absw = '/home/bulin/Mercury/'

def get_stats(lookin):
	data = dict()
	for i in xrange(len(lookin)):
		print 'For ' + lookin[i]
		folders = get_dir(lookin[i])
		folders.sort()
		noaei = need_aei(lookin[i],folders)
#		print noaei
		if noaei:
			unpack(lookin[i],noaei)
		sets = dict()
		for j in xrange(len(folders)):
			
			aeifiles = list()
			for name in os.listdir(absw+lookin[i]+'/'+folders[j]):
				if '.aei' in name: aeifiles.append(name)
			
			for thing in aeifiles:
				call_fmft(lookin[i]+'/'+folders[j],thing,6,1)
				call_fmft(lookin[i]+'/'+folders[j],thing,6,2)
#		data[lookin[i]] = sets
		#data.append([lookin[i],sets])
#	return data

#################################################
#	Navigate, check for aei, unpack		#
#################################################

#get a list of Dir inside targe directory
def get_dir(where):
	folders = []	#Initialize list
#	print '1'
	print absw + where
	contents = os.listdir(absw + where) #Get contents
	for i in xrange(len(contents)): #Iterate over contents
#		print '2'
		if os.path.isfile(absw + where +'/'+ contents[i]) != True: #If not a file, so if dir
#			print '3'
			if contents[i] in ind_names: #If a directory that matches my name format
#				print '4'
				folders.append(contents[i]) #Append
	return folders 
	
#Determine what I need unpacked
def need_aei(where,folders):
	noaei = []
	for i in xrange(len(folders)): #iterate over folders in target
		aei = False #Initialy assume that all sims have no aeis
		contents = os.listdir(absw + where + '/' + folders[i]) #Content list
		for line in contents: #Check each name for .aei
			if '.aei' in line:
				aei = True #Change state of AEI
		if aei == False: noaei.append(folders[i])
	return noaei

#Copy element6 and the needed input files then unpack
def unpack(where,noaei):
	home = os.getcwd() #So that we can return to the needed home directory where files are later
	for i in xrange(len(noaei)):
		os.system('cp ./element6 ./element.in ./message.in ' + absw + where + '/' + noaei[i])
		os.chdir(absw + where + '/' + noaei[i])
		os.system('./element6')
		os.chdir(home)
	
def call_fmft(where,filename,nfreq,mode):
	#Where am I hiding the source code
	sourcepath = '/home/bulin/Mercury/scripts/fmft/'
	absw = '/home/bulin/Mercury/'
	home_path = os.getcwd()
	os.chdir(absw + where)

	#Now find the AEI file that im inputting
	#filename = raw_input("Your AEI File (in this directory please): ")
	t,a,ecc,inc,omega,capom,capm,m,no = np.genfromtxt(filename, skip_header=4, unpack=True)
	
	#Convert from degrees to radians
	omega = omega * math.pi / 180
	capom = capom * math.pi / 180

	#Calculate longitude of pericenter and real and imaginary eccentricities
	pomega = omega + capom
	x = ecc * np.cos(pomega)
	y = ecc * np.sin(pomega)

	#Now I have to make somekind of file for the FMFT
	f = open('inputfile','w')
	if mode == 1:
		for lin in range(len(t)):
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
	power = int(math.floor(math.log(len(t),2)))
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
	os.system('./main_fmft < inputfile > '+filename.split('.aei')[0]+str(mode)+'.fmft')
	os.chdir(home_path)
