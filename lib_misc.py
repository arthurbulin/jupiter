#Misc items Library
#Based off of the Guild Wars 2 economy analysis tool by Jawamaster (Arthur Bulin)
import pickle
import os
#version: 1.0

#This just makes pickling easier. A single def to write/receive, open/return data.
def cucumber(data, name, where, which):
	if which == 'o':
		file = open(where + name,'r')
		ret = pickle.load(file)
		file.close()
		return ret
	if which == 'w':
		file = open(where + name,'wb')
		pickle.dump(data,file)
		file.close()

#For writing standard files, txt, csv, etc.
def scribe(data, name, where, which):
	if which == 'o':
		f = open(where + name,'r')
		dat = f.read()
		f.close()
		return dat
	if which == 'w':
		f = open(where + name,'w')
		f.write(data)
		f.close()
	if which == 'ol':
		with open(where + name,'r') as f:
			dat = f.readlines()
		return dat
	if which == 'wl':
		f = open(where + name, 'w')
		print >> f, "\n".join(str(i) for i in data)
		f.close()
