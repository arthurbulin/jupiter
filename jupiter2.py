import lib_merc as lme
import h5_bridge as h5b
import numpy as np
import os
import amd_collector as amc
import plot_base as pb
import AMDmonitor as amd

absw = lme.lib_get_path('absw')
data_out = lme.lib_get_path('data_out')
do_hdf5 = lme.lib_get_path('hdf5')

def main():
	found_hdf5 = False
	if os.path.isfile(data_out+'data.hdf5'):
		found_hdf5 = True
	
	while True:
		#Print menu
		print 'Jupiter Menu:'
		if found_hdf5 == False:
			print 'Data.hdf5 not found. AEI mode will be assumed if hdf5 scan is not run'
	
		print '1: hdf5 scan'
		print '2: AMD analysis'
		print '3: FMFT analysis - DISABLED'
		print '4: Survival analysis - DISABLED'
		print '5: Simulation setup - DISABLED'
		print '0: Exit'
	
		while True:
			input_v = input('>') #Get input
			if input_v == 0:
				break
			elif input_v == 1: #For hdf5 scan
				print '	To commence HDF5 scan and commit please enter the name(sim number) you would like to commit'
				print '	Enter the values seperated by a comma 1,2,3,etc.'
				hdf5_lookin = raw_input('>').split(',')
				print '	Now running HDF5 scan and commit. This may take some time depending on size and number.'
				state,conflicts = h5b.main(hdf5_lookin) #Return conflicts, not implimented yet
				break
			elif input_v == 2: #AMD analysis
				input_v = amd_analysis()
				break
			elif input_v == 3: #FMFT analysis
				input_v = fmft_analysis()
				print 'option 3'
			elif input_v == 4:
				print 'option 4'
			elif input_v == 5:
				print 'option 5'
			else: #Invalid entry handling
				print 'That is not a valid option'
	
			if input_v == 0: break
				
		if input_v == 0: break
		
def fmft_analysis():
	while True:
		print
		

##############################################################################################
#				AMD ANALYSIS ROUTINES					     #
##############################################################################################
#These routines control AMD analysis

def amd_analysis():
	"""AMD data analysis"""
	while True: 
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
				folders = h5b.get_keys(lookin)
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
