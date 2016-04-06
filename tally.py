#!/usr/bin/python
import lib_misc as lmi
import lib_merc as lme
import os
import pylab as pl
#import numpy as np
#import sys
#import warnings as war

#war.filterwarnings("ignore")
absw = lme.lib_get_absw()

def main(where):
#	number = str(sys.argv[1])
#	number = "19"
	list = os.listdir(absw + where)
	counter,information,selected,planets = {},[],[],[]
	i = 0
	
	list = sorted(list)
	for item in list:
		if os.path.isdir(absw+where+'/'+item) == False: break
		data = lmi.scribe('null','info.out',absw+where+"/"+item+"/","ol")
		things = create_info(data, "./"+item, item)
		information.append(things)

#Sort out first ejection times etc
#	print information[0][1]
	for n in information[0][1]:
		counter.update({n[0]:0})
	#print counter
	for each in xrange(len(information)):
		time = []
		planetdata = information[each][1]
		for i in planetdata:
			if "Stable" not in i[2]:
#				if "collided" not in i[2]:
#					if "ejected" not in i[2]:
				time.append(float(i[2]))
			else:
				counter[i[0]] = counter[i[0]] + 1
#				print counter	
	
		if time:
			time = sorted(time)
			first = time[0]
			selected.append(first)
			for p in planetdata:
#				print p
#				print str(first)
				if 'Stable' not in p[2]:
					if str(first) in str(float(p[2])):
#						print p[2]
						firstp = p[0]
						planets.append(firstp)

#Survival fraction calculations
#	print counter	
	for each in counter:
		counter[each] = format(counter[each] / 10.,'.2f')

	sets,final = [],[]
#Graphing and data output
#	print planets
#	print sets
	for x in planets:
		if x not in sets:
			sets.append(x)
	for y in xrange(len(sets)):
		tally = planets.count(sets[y])
#		print tally
		final.append(tally)
	fin = zip(sets, final)
	fin.append(counter)

	lmi.scribe(fin,"/first_losses_" + number+ ".out",".","wl")
	
	
	fig = pl.figure()
	ax = fig.add_subplot(111)
	n = len(selected)
	ax.hist(selected,n)
	title = "First instability times for sim " + number
	pl.title(title)
	pl.xlabel("Planets")
	pl.ylabel("Count")
	pl.savefig(title)
	
#Meat of data retrieval
def create_info(info, dir, sim_name):
	dump_num = 0
	done_success = False

	system_events,event_data,big_index,big_names = [],[],[],[]
	big_data = lmi.scribe('null','/big.in',dir,'ol')
	
	#Extract style, epoch, and name line
	for i in xrange(len(big_data)):
		line = big_data[i]
		if "style" in line:
		 	style = line.split("= ", 1)[1].split("\n",1)[0]
		if "epoch" in line:
			epoch = line.split("= ", 1)[1].split("\n",1)[0]
		if "m=" in line:
			big_index.append(i)
	#Extract the names of the big bodies
	for i in big_index:
		big_names.append(big_data[i].split()[0])
	
	#Extract mass, r, and hill radii
	for i in xrange(len(big_names)):
		line = big_data[big_index[i]]
		if "\n" in line:
			line = line.split("\n",1)[0]
			
		name = big_names[i]
		mass = line.split("m=",1)[1].split()[0]
		hill_radi = line.split("r=",1)[1].split()[0]
		density = line.split("d=",1)[1].split()[0]
	
		#Now to extract more info from the info.out, collisions and ejections.:
		for thing in info: 
			if name in thing:
				what_happened = thing.split(big_names[i],1)[1].split("at",1)[0].strip()
				when_happened = thing.split(big_names[i],1)[1].split("at",1)[1].split(" years",1)[0].strip()
				if "collided" in what_happened:
					what_happened = "collided"
				event_data = [name, what_happened, when_happened]
		if event_data:
			if event_data[0] != name:
				event_data = [name, "Stable", "Stable"]
		else:
			event_data = [name, "Stable", "Stable"]
		
		system_events.append(event_data)
	
	return [sim_name, system_events]


main()
