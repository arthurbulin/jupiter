#This is a library file for the Mercury comprehension subroutines
#Arthur Bulin 112828967	

import os

#This definition is very very important for every other program
#This sets the ABSolute Working directory for jupiter from the file absw.path
def lib_get_absw(mode=0):
	if mode == 0:
		with open('absw.path','r') as f: absw = f.read()
	if mode == 1:
		absw = raw_input('Mercury working directory absolute path: ')
	return absw.strip()

#Used to create the reference names for folders so that anything that doesnt meet the 0...9 etc scheme isn't 
#scanned. This is currently only good for 10 sims (0-9)
def lib_ind_names(num=10):
	ind_names = range(num)
	for i in ind_names:
		ind_names[i] = str(i)
	return ind_names

#These calls set these global variables when the library is imported
ind_names = lib_ind_names()
absw = lib_get_absw()

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
		os.system('cp ./element6 ./element.in ./message.in ' + absw + where + '/' + noaei[i])
		os.chdir(absw + where + '/' + noaei[i])
		os.system('./element6')
		os.chdir(home)
