import h5py as h5 
import numpy as np
import os
import subprocess
import lib_merc as lme
import shutil


#absw = '/home/alexander/Projects/mercury_src/'
#absw = lme.lib_get_absw()
ind_names = lme.lib_ind_names()
#dat_out = lme.lib_get_out()
absw = lme.lib_get_path('absw')
data_out = lme.lib_get_path('data_out')
filename = 'data.hdf5'

##############################################################
##	Data collection and commitment in this section	     #
##############################################################

#Utilizes a python subprocess to capture the data necessary
def element_capture(cmd,where,sim,set):
	"""
	Calls the element fortran process and returns a list of all of our data.
	cmd should be the name and location of the element program. Should be same directory
	"""
	hm_dir = os.getcwd()
	os.chdir(where+sim+'/'+set)
	#Spawn the subprocess
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	#Create the list to collect
	stdout = list()
	while True:
		line = p.stdout.readline() #Get each line
		stdout.append(line) #Append each line
		if line == '' and p.poll() != None: break #When to end the loop
	os.chdir(hm_dir)
	return stdout
	
def get_header(dat):
	"""Parse the header data and return a list of the values"""
	data = dict()
	header = dat[0]
	values = header.split()
	for h in xrange(len(values)): 
		#Remove the pesky (years) in the header
		if 'years' in values[h]:
			values.pop(h)
			break
	return values	

def get_bodies(dat):
	"""Returns the bodies in the simulation, assumes all bodies exist in the begining"""
	bodies = list()
	for i in xrange(len(dat)):
		if dat[i] not in bodies:
			bodies.append(dat[i])
		else: break
	return bodies

def get_indexs(body_index, bodies):
	"""return a dictionary with keys of the bodies and the data is a list of the indexes for each body"""
	set = dict()
	for i in xrange(len(bodies)):
		temp = np.where(body_index == bodies[i])
		set[bodies[i]] = temp[0]
	return set

def refine_raw(dat):
	"""Refine raw data into usable information and return it"""
	header = get_header(dat) #Get header
				
	size = len(header) - 1
	cols = np.linspace(1,size,num=size,dtype=int) #Establish usable columns
	type = np.dtype(np.float64) #Establish a type for the values
	x = np.genfromtxt(dat[1:],usecols=cols,dtype=type) #sort our data out nicely
	
	body_set = np.genfromtxt(dat[1:],usecols=(0),dtype='str') #Retreive the bodies from the raw data
	bodies = get_bodies(body_set) #Get the bodies
	index = get_indexs(body_set, bodies) #Get the indexes of the bodies data
	
	#Get rid of the 'id' in the header
	for i in xrange(len(header)):
		if 'id' in header[i]:
			header.pop(i)
			break
			
	return header,bodies,index,x

def assemble_sets(header,bodies,inds,dat,sim,set):
	"""Sorts and commits the data to the HDF5 file"""
	data_file = h5.File(data_out+'data.hdf5','a')
	conflicts = list()
	same = None
	#Iterate over data
	for i in xrange(len(bodies)):
		index = inds[bodies[i]]
		
		#Array manipulation
		body_data = dat[index]
		body_data_rot = np.rot90(body_data)
		body_data_flip = np.flipud(body_data_rot)
		for j in xrange(len(header)):
			commit_dat = body_data_flip[j]
			path = sim+'/'+set+'/'+bodies[i]+'/'+header[j]
			
			#Had the create exception here because sometimes bad things happen wierdly
			try:
				diff = (commit_dat-np.asarray(data_file[path])).any()
			except:
				diff = True
				
			#Conflict resolution
			if path not in data_file: #If it doesnt exist, commit it to file
				data_file.create_dataset(path, data=commit_dat)
			
			elif diff: #If it is in file but does not match append
				conflicts.append(path)
			
			else: same = True #If datagroup exists and matches
	
	data_file.close()
	
	if len(conflicts) > 0: return conflicts #Return path list of conflicts
	elif same != None: return True #If there are conflicts but data is the same in the file return True
	else: return False #No conflicts, all writes sucessfull
	
def check_dir(where,sim):
	"""Gets sim/set contents and copies needed files over"""
	#shutil is used here as it is a high-level operation function and will maintain most metadata and permissions during copy.
	set_list = os.listdir(where+sim)
	sets = list()
	for i in xrange(len(set_list)):
		if os.path.isdir(where+sim+'/'+set_list[i]) == True and set_list[i] in ind_names:
			sets.append(set_list[i])
			dir_list = os.listdir(where+sim+'/'+set_list[i])
			if 'element.x' not in dir_list:
				shutil.copy(where+'jupiter/hd5_bridge/element.x',where+sim+'/'+set_list[i]+'/')
			if 'element.in' not in dir_list:
				shutil.copy(where+'jupiter/hd5_bridge/element.in',where+sim+'/'+set_list[i]+'/')
			if 'mercury.inc' not in dir_list:
				shutil.copy(where+'jupiter/hd5_bridge/mercury.inc',where+sim+'/'+set_list[i]+'/')
			if 'files.in' not in dir_list:
				shutil.copy(where+'jupiter/hd5_bridge/files.in',where+sim+'/'+set_list[i]+'/')
			if 'message.in' not in dir_list:
				shutil.copy(where+'jupiter/hd5_bridge/message.in',where+sim+'/'+set_list[i]+'/')
	return sets


def main(lookin):
	total_conflicts,conflicts_bool = list(),list()
	
	for i in xrange(len(lookin)):
		print 'Running for ' + lookin[i]
		sets = check_dir(absw,lookin[i])
		sets.sort()
		print 'Sets: ',
		
		for j in xrange(len(sets)):
			print sets[j],
		
			raw = element_capture('./element.x',absw,lookin[i],sets[j]) #Get raw data
			header,bodies,index,x = refine_raw(raw) #Refine data and get header, bodies, indexes, and data(x)
			conflicts = assemble_sets(header,bodies,index,x,lookin[i],sets[j]) #Assemble sets and return conflicts

			if type(conflicts) != bool: total_conflicts.append(conflicts) #if type != bool then append
			else: conflicts_bool.append(conflicts) #if  type == bool then get bool state and append
		
	#Conflict resolution
	if len(total_conflicts) > 0: #if there is a length to total_conflicts 
		print ' WARNING: Conflicts exist', #print alert of conflicts
		state = False #set state to false
		if True in conflicts_bool: #Find out it there were also matching data conflicts
			print ' SOME existing data matched!' #Alert if so
			state = True #Change state
		return state,total_conflicts #Return state of conflicts and list if necessary
			
	elif True in conflicts_bool:
		return True,[] #If there were same conflicts but no diffs
		
	else: return False,[] #No conflicts at all

def retreive(sim,set,world,value):
	"""Returns a dataset from our hdf5 file"""
	f =  h5.File(data_out+filename,'r')
	try:
		retreived = f[sim+'/'+set+'/'+world+'/'+value]
		retreived = np.array(retreived)
		f.close()
		return retreived
	except:
		print 'WARN: A value for ' + str(sim +'/'+set+'/'+world+'/'+value) + ' does not exist!!!'
		f.close()
		return None
		
def get_keys(sim,set=None,world=None):
	"""returns the keys in a specific group or subgroup"""
	f = h5.File(data_out+filename,'r')
	if set == None and world == None:
		return [str(i) for i in f[sim].keys()]
	elif world == None:
		return [str(i) for i in f[sim+'/'+set].keys()]
	else:
		return [str(i) for i in f[sim+'/'+set+'/'+world].keys()]


