#This program will scan a directory and load in Mercury data. It will also generate and submit to condor.
#Also it will write and store information as binary files.
#Test
import os
import jawalib as jl #This will import the JawaLib. It is a series of defintions that I use for a number of programs.
import create_info as ci
#import numpy as np

def main():
	if os.path.isfile("./mercdir.txt") == True:
		dir = jl.scribe('null',"/mercdir.txt",".","o")
	else:
		dir = raw_input("Enter your Mercury directory relative to Jupiter: ")
		jl.scribe(dir,"/mercdir.txt",".","w")
		
	#print scan(dir)
	if os.path.isfile('./jupiterdb.pickle') == False:
		first_run_opts(dir)
	else:
		print "Go away~ This isnt done yet~ Bye~"
		exit("Shhhh~~")		


#Start by scanning the main mercury directory
def scan(dir):
	list = os.listdir(dir)
	list_info = []
	if 'jupiter' in list: list.remove('jupiter')
	if 'test_jupiter' in list: list.remove('test_jupiter')
	for i in list:
		if '.' in i: list.remove(i)
	list1 = sorted(list)
	return list1

#This will run on an absolute first run scan	
def first_run_opts(dir):
	print "Sorry, but it seems Jupiter hasn't found a previous database."
	print "To procede I will need to run a scan of the directory above this one."
	print "It should be your Mercury directory. Depending on number of simulations and size of data this might take a bit."
	print "If you procede there will be a few options for you."
	print "You can choose these options: "
	print "\t 1: Run the scan with full options input"
	print "\t 2: Run a quick scan. This will supress user input options and only load the basics"
	print "\t 3: Run for a single selection simulation"
	print "\t 4: quit"

	input = raw_input("Option: ")
	
	if input == '1':
		full_first(dir)
	if input == '2':
		quick_first(dir)
	if input == '3':
		single_run()
	if input == '4':
		exit()

#first full run will have user options
def full_first(dir):
	dir_list = scan(dir) #Gives list of simulation directories
	print "I have " + str(len(dir_list)) + " directories in the specified mercury folder. Let us start from the first."
	for item in dir_list:
		print "\n Directory: " + item
		temp_dir = dir + "/" +  item
		
		#Get some file states
		db_present = os.path.isfile(temp_dir + "/" + item + ".pdb")
		desc_present = os.path.isfile(temp_dir + "/description.txt")
		
		if db_present == False: #IF pdb doesnt exist
			
			if desc_present == False: #If description doesnt exist
				make_description = raw_input("Would you like to create a description for this simulation?\n If yes nano will open. When done CTRL + x to return to the program. y/n: ")
				if make_description == 'y':
					os.system("nano " + temp_dir + "/description.txt")
				#jl.scribe('skipped',"/description.txt",temp_dir,"w")
			
			else:
				desc = jl.scribe('null',"/description.txt",temp_dir,"o")
				print "This simulation has an associated destription: \n"
				print desc.rstrip("\n")
				print "\n"
				edit_desc = raw_input("Would you like to edit this description? If yes nano will open. When done CTRL+X to return to the program. y/n: ")
				if edit_desc == 'y':
					os.system("nano " + temp_dir + "/description.txt")

		else:
			if desc_present == True:
				print "I found a database already for this simulation and a description.txt"
				review_it = raw_input("Would you like to reveiw the description? y/n ")
				if review_it == 'y':
					desc = jl.scribe('null',"/description.txt",temp_dir,"o")
					print "\n" + desc
					change_it = raw_input("Would you like to change it? y/n ")
					if change_it == 'y':
						os.system("nano " + temp_dir + "/description.txt")
					print "I have also found a previous database file: " + item + ".pdb"
					while True:
						refresh_it = raw_input("Would you like to refresh it? y/n ")
						if refresh_it != 'n' or refresh_it != 'y': print("yes or no? ")
						else: break
					if refresh_it == 'n': break
			else:
				print "I have found a database but no description.txt"
				make_one = raw_input("Make a description? y/n")
				if make_one == 'y':
					os.system("nano " + temp_dir + "/description.txt")
				while True:
					refresh_it = raw_input("Would you like to refresh the database? y/n ")
					if refresh_it != 'n' or refresh_it != 'y': print("yes or no? ")
					else: break
				if refresh_it == 'n': break
					
		
		collated_data = []
		
		which = raw_input("Is this directory filled with runs(1) or sets of runs(2)? ")
		if which == '1':
			runs_list = scan(temp_dir)
			for run in runs_list:
				sub_run_dir = temp_dir + "/" + run
				info = jl.scribe('null',"/info.out",sub_run_dir,'ol')
				#Call creat_info from it's own little file.
				#I put it there because it is fucking long and I hate long ugly code.
				#Imports are better because this isnt 1999 and I don't want it all obfuscated
				info_data = ci.create_info(info, sub_run_dir, item + "/" + run)
				collated_data.append(info_data)
				
				#exit("This has been a test")
			jl.cucumber(collated_data, "/" + item + ".pdb", temp_dir, 'w')
			print item + ".pdb written to directory."
				 
		if which == '2':
			print "Nothing to see here~ Other than unfinished code~"
			exit("Shhh~~ Breath deep...")


main()
