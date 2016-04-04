import AMDmonitor as amd
import os
import numpy as np

#which sims do i look in, need list of strings
ind_names = []
for i in xrange(10):
	ind_names.append(str(i))

#Set my absolute directory. Prevents odd relative errors. include / in the end or it will break
absw = '/home/bulin/Mercury/'
#lookin = ['31']

def get_stats(lookin):
	data = dict()
	peaks_to_check = [2.5,5,10]
	for i in xrange(len(lookin)):
		print 'For ' + lookin[i]
		folders = get_dir(lookin[i])
		folders.sort()
		noaei = need_aei(lookin[i],folders)
		if noaei:
			unpack(lookin[i],noaei)
		sets = dict()
		for j in xrange(len(folders)):
		 	print 'Getting AMD for ' + lookin[i] + ':' + folders[j],
			t,am = amd.AMDmonitor(absw + lookin[i] + '/' + folders[j])
			print 'Getting Max AMD',
			max = amd_max(t,am)
			print 'Getting peaks'
			peaks = amd_first_times(t,am,peaks_to_check)

			sets[folders[j]] = {'max':max, 'peaks':peaks}
		data[lookin[i]] = sets
		#data.append([lookin[i],sets])
	return data

#################################################
#	Navigate, check for aei, unpack		#
#################################################

#get a list of Dir inside targe directory
def get_dir(where):
	folders = []	#Initialize list
	contents = os.listdir(absw + where) #Get contents
	for i in xrange(len(contents)): #Iterate over contents
		if os.path.isfile(absw + where +'/'+ contents[i]) != True: #If not a file, so if dir
			if contents[i] in ind_names: #If a directory that matches my name format
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

#########################################
#	AMD Stats that we want to get	#
#########################################

def amd_max(t,am):
	peak = 0
	for i in xrange(len(am)-1):
		if am[i+1] > am[i]:
			peak = am[i+1]
			time = t[i+1]
	return {'time':time, 'peak':peak}

def amd_first_times(t,am,peaks):
	d = dict()
	for each in peaks: #for each value in peaks
		for i in xrange(len(am)): #Now check all of the amd values for comparison
			if am[i] >= each:
				d[each] = {'time':t[i], 'amd':am[i]}
				break
	return d

#Not update for use with dictionaties
def dat_out(data):
	if data is dict(): print('Not updated'); return None
	with open('amd.dat','w') as f:
		for i in xrange(len(data)):
			for j in xrange(len(data[i][1])):
				init_str = str(data[i][0]) + ':'+ str(data[i][1][j][0]) + ',' + str(data[i][1][j][1][0]) +','+ str(data[i][1][j][1][1])
				for k in xrange(len(data[i][1][j][2])):
					init_str = init_str + ',' + str(data[i][1][j][2][k][1]) + ',' + str(data[i][1][j][2][k][2])
				f.write(init_str+'\n')

def get_amd_data(lookin):
	time,amd = list(),list()
	for i in xrange(len(lookin)):
		a,b = ret_median(lookin[i])
		time.append(a)
		amd.append(b)
	return time,amd

#This will return median values across a single simulation
def ret_median(sim):
	#Get my directory structures
	folders = get_dir(sim)
	folders.sort()
	
	#Need AEI? Unpack
	noaei = need_aei(sim,folders)
	if noaei:
		unpack(sim,noaei)
	
	#Get amd values and time
	med_sets,t_sets = list(),list()
	for i in xrange(len(folders)):
		t,am = amd.AMDmonitor(absw + sim + '/' + folders[i])
		med_sets.append(am)
		t_sets.append(t)
	
	set_lens = list()
	for k in xrange(len(t_sets)):
		set_lens.append(len(t_sets[k]))
	time = t_sets[set_lens.index(max(set_lens))]
	new_amd = make_single_list(med_sets)
	return time,new_amd

def make_single_list(sets):
	temp = list()
	for i in xrange(len(sets)):
		temp.append(len(sets[i]))
	temp.sort(reverse=True)

	new_amd = list()
	for i in xrange(temp[0]):
		meds = list()
		for j in xrange(len(sets)):
			try: meds.append(sets[j][i])
			except: continue
		new_amd.append(np.median(meds))
	return new_amd
