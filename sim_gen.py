import os
import pl_gen as pg

def main():
	#Set dir or change it
	print("=======CREATE SIMULATION========")
	current_dir = os.getcwd()
	print("Your current working directory is "+ current_dir)
	change = raw_input("Would you like to change it?")
	if change == 'y':
		current_dir = raw_input("Please use non-relative directory: ")
	
	#Main program run
	sim_name = raw_input("Please choose a name for the simulation. No spaces please: ")
	print("Making directory")
	os.system("mkdir " + current_dir +"/"+ sim_name)
	current_wdir = current_dir + "/" + sim_name
	how_many = raw_input("How many simulation runs would you like: ")
	
	#Create base simulation for copying and creating
	print("creating base simulation directory")
	os.system("mkdir " + current_wdir + "/0") 
	copy_files(current_wdir+"/0",0)
	arg_changes = dict(set_default_args())
	
	#Start the manipulation
	while True:
		print "\nFor which of the following would you like to alter the args? "
		for key in arg_changes: print key + " | ",
		choice = raw_input("> ")
		#If planet is default then start the arg mod for it
		if choice in arg_changes:
			print "\n Argument modification for " + choice
			for arg in arg_changes[choice]: print arg + " | ",
			
			while True:
				choose_arg = raw_input("> ")
				#If arg is one of the args then start modification for it
				if choose_arg in arg_changes[choice]:
					#Stops bad things from happening when a user enters a string that isnt a float
					try: arg_changes[choice][choose_arg] = float(raw_input("modifier> "))
					except: print "Something went wrong. oops~ Check your syntax."
					break
				#Let's me short the loop and exit the system
				if choose_arg == "kill": exit()
				#Lets me back up
				if choose_arg == "back": break				
				else: print "Argument specified is not a valid option, please choose from the list."
			break
		if choice == "kill": exit()
		else:
			print "Choice is not a valid option, please choose one from the list."
	print "Generating big.in file"
	break #Remove this later, it is just to keep it from running the loop but allows me to not have to indent later
	#Generate the param.in file
	


	pg.pl_gen(arg_changes,current_wdir+"/0")
			
def copy_files(where,which=0):
	if which == 0:
		os.system("cp " + "-p ./mercury/* " + where)
#		os.system("

def set_default_args():
	arg_changes = dict()
	default_vals = {'mass':1,'a':1, 'ecc':1, 'inc':1, 'longper':1, 'longasc':1, 'meanlong':1}
	planets = ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn']
	for each in planets:
		arg_changes[each] = default_vals
	return arg_changes

main()
