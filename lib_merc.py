#This is a library file for the Mercury comprehension subroutines
#Arthur Bulin 112828967	

import os

#This definition is very very important for every other program
#This sets the ABSolute Working directory for jupiter from the file absw.path
#def lib_get_absw(mode=0):
#	"""Returns our Absolute working path defined in params.cfg"""
#	if mode == 0:
#		contents = lib_read_params()
#		for i in xrange(len(contents)):
#			if 'absw:' in contents[i]:
#				absw = contents[i].split(':')[1]			
#	if mode == 1:
#		absw = raw_input('Mercury working directory absolute path: ')
#	return absw.strip()

#Used to create the reference names for folders so that anything that doesnt meet the 0...9 etc scheme isn't 
#scanned. This is currently only good for 10 sims (0-9)
def lib_ind_names(num=10):
	"""Returns a list of 0-9 strings, used for set folder naviagation, can be altered for other values, but default is 10"""
	ind_names = range(num)
	for i in ind_names:
		ind_names[i] = str(i)
	return ind_names

#Gets our data out directory. This will determine where all data and subfolders are stored
#def lib_get_dat_out(mode=0):
#	"""Returns the string path for data output"""
#	if mode == 0:
#		contents = lib_read_params()
#		for i in xrange(len(contents)):
#			if 'data_out:' in contents[i]:
#				data_out = contents[i].split(':')[1]
#	return data_out

def lib_get_path(path,mode=0):
	if mode == 0:
		contents = lib_read_params()
		for i in xrange(len(contents)):
			if path in contents[i]:
				gets = contents[i].split(':')[1].split()[0]
	return gets
		
def lib_read_params():
	"""This will read in our params.cfg file and return them as a list"""
	with open('params.cfg','r') as f:
		contents = f.readlines()
	return contents
			



#These calls set these global variables when the library is imported
ind_names = lib_ind_names()
#absw = lib_get_absw()
absw = lib_get_path('absw')

#################################################
#	Navigate, check for aei, unpack		#
#################################################

#get a list of Dir inside targe directory
def lib_get_dir(where):
	folders = []	#Initialize list
	print absw + where
	contents = os.listdir(absw + where) #Get contents
	for i in xrange(len(contents)): #Iterate over contents
		if os.path.isfile(absw + where +'/'+ contents[i]) != True: #If not a file, so if dir
			if contents[i] in ind_names: #If a directory that matches my name format
				folders.append(contents[i]) #Append
	return folders 
	
#Determine what I need unpacked
def lib_need_aei(where,folders):
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
def lib_unpack(where,noaei):
	home = os.getcwd() #So that we can return to the needed home directory where files are later
	for i in xrange(len(noaei)):
		os.system('cp ' +absw+'jupiter/mercury/element6 '+absw+'jupiter/mercury/element.in '+absw+'jupiter/mercury/message.in ' + absw + where + '/' + noaei[i])
		os.chdir(absw + where + '/' + noaei[i])
		os.system('./element6')
		os.chdir(home)
