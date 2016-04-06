#!/usr/bin/ipython27
#Arthur Bulin 01023806210 
import pylab
import numpy as np
from matplotlib.ticker import AutoMinorLocator
import astropy.constants as const

#x1 and d are list type, or nparray type
def plot_base(x1,d,savename=None,type=1,dolegend=False,names=None,yaxis_title=None,xaxis_title=None,title=None,x_limit=None,y_limit=None,set_dpi=128):

	minorLocator = AutoMinorLocator()

	#Create the figure and a subplot
	fig = pylab.figure(1,dpi=set_dpi)
	ax1 = fig.add_subplot(1,1,1)
	
	#Prevents pylab plot from clearing the figure each successive time I call plot
	pylab.hold(True)

	#Iterate through for each array in the list d and add it to the plot
#		ax1.plot(x1,d[i],linestyle=linestyles[i],label=labels[i],lw=2)

	if type == 1:
		if names is not None:
			for i in xrange(len(d)):
				ax1.plot(x1,d[i],label=names[i],lw=2)
		else:
			for i in xrange(len(d)):
				ax1.plot(x1,d[i],lw=2)
	if type == 2:
		for i in xrange(len(d)):
			ax1.hist(d[i])

	#Assign Axis labels, title, and ticks
	if yaxis_title is not None: ax1.set_ylabel(yaxis_title,fontsize=18)
	if xaxis_title is not None: ax1.set_xlabel(xaxis_title, fontsize=18)
	if title is not None: ax1.set_title(title)
	ax1.xaxis.set_minor_locator(minorLocator)
	
	if dolegend == True: ax1.legend() #Generate legend, location can be changed but this works with the current graph

	#Set Axis limits to make it more readable and less wasteful
	if x_limit is not None: pylab.xlim(x_limit)
	if y_limit is not None: pylab.ylim(y_limit)

	#Few more ticks and the grid
	pylab.tick_params(which='both', width=2)
	pylab.tick_params(which='major', length=7)
	ax1.xaxis.grid(True,which='both',linewidth=.5)

	if savename is not None:
		pylab.savefig(savename)
	else:
		pylab.show() #Show
		
	fig.clf()
