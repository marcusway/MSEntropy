# homemade_mse.py

# This is just a collection of functions to 
# help visualize the coarse-graining process
# in multi-scale entropy calculation

from __future__ import division
import numpy as np

def coarse_grain(x):

	'''
	This function takes as input a time-series, 
	x, and returns a list of lists, coarse_grains, 
	coarse_grains[i] corresponds to the time-series,
	x, coarse-grained at scale i.  The multi-scale
	entropy algorithm, as implemented by Bill Bosl in mse.so
	works by calculating the sample entropy of successive 
	coarse-grained series.  For example, the entropy at scale
	5 of x is equivalent to the sample entropy of the 
	sequence given by coarse_grain[5]. The 'print' commands
	are commented out, but provide a little more information
	on the process. 
	'''
	coarse_grains = []
	for scale in range(1,len(x)//5):
		#print 'Coarse Graining at Scale', scale, '...\n'
		#print [x[j:j+scale] for j in range(0,len(x)-scale+1,scale)]
		# Coarse-graining achieved by averaging every 'scale' values together
		coarse_grains.append([np.mean(x[j:j+scale]) for j in range(0,len(x)-scale+1,scale)])
		#print coarse_grains[-1]
		
	return coarse_grains

def coarse_indices(x):
	'''
	This just uses the coarse_grain function
	to generate a coarse grainings of the 
	sequence [0,1,2,3...len(x)-1].  This is useful
	in plotting coarse grainings of x because 
	it tells you to which time point
	in the original series a value in a coarse
	grained series corresponds.  In other words,
	while x can just be plotted against [0,1,2..len(x)-1],
	coarse_grains[i] should be plotted against 
	coarse_indices[i]. 
	'''
	return coarse_grain(range(len(x)))

def coarse_fig(x):

	'''
	This function generates and saves 
	plots of successive coarse grainings
	and corresponding sample entropies
	of the input time series, x.  I used
	this to generate the graphs used
	for the much acclaimed short film,
	"Entropy at Many Scales"  
	'''
	import matplotlib.pyplot as plt
	import mse
	signal = coarse_grain(x)
	domain = coarse_indices(x)
	msentropy = mse.mse(x, np.zeros(len(x)/5))
	for scale in range(0,len(signal)):
		fig = plt.figure()
		
		# Make the time series graph on top
		fig.add_subplot(2,1,1)
		plt.plot(domain[scale], signal[scale])
		plt.ylim(min(x),1.2*max(x))
		plt.title('Scale ' + str(scale))
		plt.xticks([])
		plt.yticks([])
		plt.xlabel('Time')
		plt.ylabel('Voltage')
		
		# And the entropy bar graph on bottom
		fig.add_subplot(2,1,2)
		plt.barh(1,msentropy[scale],1,align = 'center', color = 'r')
		plt.xlabel('Sample Entropy')
		plt.yticks([])
		plt.ylim(0,2)
		plt.xlim(0,max(msentropy))
		
		# Save the figure
		file_title = '../graphs/CG_graphs/cg_scale_' + str(scale) + '.png'
		print 'saving ', file_title
		plt.savefig(file_title)
		plt.close()
	
	
