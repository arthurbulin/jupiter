import lib_merc as lme
import h5_bridge as h5b
import numpy as np
import os
import amd_collector as amc
import plot_base as pb
import AMDmonitor as amd
import fmft_run as ffr
import generate_from_base as gfb

absw = lme.lib_get_path('absw')
data_out = lme.lib_get_path('data_out')
do_hdf5 = lme.lib_get_path('hdf5')

def main():
	found_hdf5 = False
	if os.path.isfile(data_out+'data.hdf5'):
		found_hdf5 = True
	
	while True:
		os.system('clear')
		#Print menu
		print 'Jupiter Menu:'
		if found_hdf5 == False:
			print 'Data.hdf5 not found. AEI mode will be assumed if hdf5 scan is not run'
	
		print '1: hdf5 scan'
		print '2: AMD analysis'
		print '3: FMFT analysis - Partialy Operational'
		print '4: Survival analysis - DISABLED'
		print '5: Simulation setup - DISABLED'
		print '0: Exit'
	
		while True:
			input_v = input('>') #Get input
			if input_v == 0:
				return 'Goodbye'
			elif input_v == 1: #For hdf5 scan
				print '	To commence HDF5 scan and commit please enter the name(sim number) you would like to commit'
				print '	Enter the values seperated by a comma 1,2,3,etc.'
				hdf5_lookin = raw_input('>').split(',')
				print '	Now running HDF5 scan and commit. This may take some time depending on size and number.'
				state,conflicts = h5b.main(hdf5_lookin) #Return conflicts, not implimented yet
				delay = raw_input('Hit enter to continue')
				break
			elif input_v == 2: #AMD analysis
				input_v = amd_analysis()
				break
			elif input_v == 3: #FMFT analysis
				input_v = fmft_main_menu()
				break
			elif input_v == 4:
				print 'option 4'
				break
			elif input_v == 5:
				input_v = sim_gen_main()
				break
			else: #Invalid entry handling
				print 'That is not a valid option'
	
		if input_v == 0: return

##############################################################################################
#			Simulation generation routines					     #
##############################################################################################
def sim_gen_main():
	while True:
		print "Simulation Generation Menu"
		print "1: Set custom values and generate"
		print "2: Generate Default value simulation"
		print "3: Generate Condor job"
		print "4: Generate description and values file"
		print "5: Exit to JUPITER menu"
		print "0: Exit JUPITER"
		
		while True:
			input_v = input('>')
			
			if input_v == 0: #program exit
				return input_v
			elif input_v == 1: #Generate a sim with custom values
				input_v = sim_gen_custom()
				break
			elif input_v == 2:
				sim_name = raw_input("Simulation Name: ")
				gfb.main()		
			elif input_v == 3:
				print "3"
			elif input_v == 4:
				print "4"
			elif input_v == 5:
				return None
			else:
				print "That is not a valid option"
#Option 2
def gen_sim(mode=0):
	if mode == 0:
	#	args = gfb.set_default_args()
	#	params = gfb.params_default()
		input_v,params,name,gen = param_set_menu()
	#if mode=1:				
	return input_v,params,name,gen

#Params menu for settings values for ALL SIMULATIONS no matter the choice
def param_set_menu():
	params = gfb.param_defaults()
	while True: #get name and make them do it right
		name = raw_input("Simulation Name: ")
		if ' ' in name:
			print "Don't use spaces, cause idk what'll happen. I didn't plan for them"
		elif '/' in name:
			print "No slashes, try again"
		else:
			break
			
	while True: #Gets number of generations and corrects for non ints
		gen = raw_input("Number of Simulations: ")
		try: 
			gen = int(gen)
			if gen == 0:
				print "0 is not valid"
			else:
				break
		except:
			print "Please enter a useable integer value"

	#get param types
	param_types = dict()
	for i in params.keys():
		param_types[i] = type(params[i])

	os.system('clear')
	print "Most of these params will not need changed"
	print "1: will will adjust the basics."
	print "2: adjust all options"
	print "3: return without params"
	print "0: Exit Mercury"
	
	while True:
		input_v = input('> ')
		
		if input_v == 0:
			#return and exit JUPITER
			return 0,None,None,None
		elif input_v == 1:
			do_these = ['timestep','interval','stop','user force']
			break
		elif input_v == 2:
			do_these = param.keys()
			break
		elif input_v == 3:
			#Return to the menu with no params
			return 77,None,None,None
		else:
			print "That is not a valid option"
	
	#Get the user's input and make sure it is legit usable
	for i in xrange(len(do_these)):
 		while True:
	 		print "Setting " + do_these[i]
 			print "This must be of type: "+ str(param_types[do_these[i]]).split("'")[1]
			value = raw_input('> ')
			if type(value) == param_types[do_these[i]]: #Check its of the right type
				break
			else:
				try: 
					value = param_types[do_these[i]](value) #Try to cast it to proper type and see if it is input's fault
					break
				except: print "Problem with that value\n"
				
		params[do_these[i]] = value #Commit value to params
	
	return 88,params,name,gen
				
				
				
##############################################################################################
#				FMFT OPERATIONS						     #
##############################################################################################
#These routines will operate the FMFT

def fmft_main_menu():
	while True:
		os.system('clear')
		#Print menu
		print '	FMFT Menu'
		print '1: Run FMFT'
		print '2: Analyze FMFT - DISABLED'
		print '3: Exit to Main MENU'
		print '0: Exit'
		
		while True:
			input_v = input('>') #User input

			#Exit Mercury
			if input_v == 0: 
				return 0
			#Run options
			elif input_v == 1:
				not_stored = list()
				
				print "Full time period(2) or halfs?(1)"
				mode_v = input('>')
				if mode_v == 0: return 0
				
				print "Please input simulation names seperated by a comma: "
				sims = raw_input('>').split(',')
				
				#This checks for data not present
				if do_hdf5 == 'true':
					sim_stored = h5b.get_keys()
					for i in xrange(len(sims)):
						if sims[i] not in sim_stored:
							not_stored.append(sim[i])
					if len(not_stored) > 0:
						print 'These simulations were not found, please find the data'
						for j in not_stored:
							print j,
						break
						
				input_v = ffr.main(sims,mode=mode_v)
				break
				if input_v == 88:
					print 'Complete, no Errors'
					break
			elif input_v == 3:
				return 77
				
##############################################################################################
#				AMD ANALYSIS ROUTINES					     #
##############################################################################################
#These routines control AMD analysis

def amd_analysis():
	"""AMD data analysis"""
	while True: 
		os.system('clear')
		#Print menu
		print '	AMD Analysis'
		print '1: Return Peaks'
		print '2: AMD Max'
		print '3: Plot'
		print '4: Exit to main'
		print '0: Exit'
		
		while True:
			input_v = input('>')
			
			if input_v == 0: break
			
			elif input_v == 1: #For peaks
				peaks = [2.5]
				print 'Enter the sims you wish to look at seperated by a comma'
				lookin = raw_input('Simulations: ').split(',')
				
				print 'Enter the AMD peak. d for default: 2.5'
				peaks_get = raw_input('AMD peaks to find: ').split(',')
				#Detect defaults
				if 'd' in peaks_get:
					peaks_get = peaks
				else: #Exception handling for non defaults
					try: peaks_get = [float(x) for x in peaks_get]
					except: 
						print 'ERROR: Enter a valid number.' 
						break
				data = amc.main(lookin,peaks=peaks_get) #Actualy get the data
				
				#Print it out
				for sim in data:
					print sim+':'
					for set in data[sim]:
						print '\t'+set+': ',
						for peak in data[sim][set]['peaks']:
							print str(peak)+': '+ str(data[sim][set]['peaks'][peak]['amd']) +' at '+str(data[sim][set]['peaks'][peak]['time'])
					raw_input('\nENTER') #pause
				break	#Break the loop
								
			#FOr AMD max
			elif input_v == 2:
				print 'Enter the sims you wish to look at seperated by a comma'
				lookin = raw_input('Simulations: ').split(',')
				
				data = amc.main(lookin) #Get data
				
				#for each sim print the data
				for sim in data:
					print sim+':'
					for set in data[sim]:
						print '\t'+set+': '+ str(data[sim][set]['max']['peak']) +' at '+str(data[sim][set]['max']['time'])
					raw_input('\nENTER') #Pause
				break				
					
			elif input_v == 3: #For graphing menu
				input_v = amd_graphing()
				break
				
			elif input_v == 4:
				return None
			else:
				print 'That is not a valid option'
			#For while break and quit states
			if input_v == 0: break
		
		if input_v == 0: return 0



def amd_graphing():
	"""Graphing features"""
	while True:
		os.system('clear')
		#Print menu
		print '\tAMD Graphing Menu'
		print '1: Median Values'
		print '2: Sets Values'
		print '3: Exit Graphing'
		print '0: Exit'
		
		while True:
			input_v = input('>')		
		
			if input_v == 1:
				print '\tMedian Values Grpahing'
				print 'Enter the Simulations you wish to graph sperated by a comma.'
				lookin = raw_input('Simulations: ').split(',')
				times,medians = amc.get_amd_data(lookin)
				#plot
				pb.plot_base(times,medians,dolegend=True,names=lookin,xaxis_title='Time (years)',yaxis_title='AMD (Normalized)',title='Average AMD Values')
				break
			elif input_v == 2:
				print '\tSets Values Graphing'
				lookin = raw_input('Enter a single simulation: ')
				folders = h5b.get_keys(sim=lookin)
				folders.sort()
				
				time,amd_v = list(),list()
				for i in xrange(len(folders)):
					tt,amdd = amd.AMDmonitor(lookin,folders[i])
					time.append(tt)
					amd_v.append(amdd)
					
				pb.plot_base(time,amd_v,title='AMD values for '+lookin,xaxis_title='Time (years)',yaxis_title='AMD (Normalized)',names=folders)
				break
			elif input_v == 3:
				return None
			elif input_v == 0:
				return 0
				#return input_v

main()
