
""""
Reads all time series files and saves the FOCUS channel electrode data 
to a dictionary, which is saved as a shelve database. Subjects originally 
sampled at 500Hz are downsampled in this procedure.  
"""
import os
import numpy as np
import shelve
import cPickle as pickle
from data_manipulation import get
from collections import defaultdict

FOCUS_Electrodes = {'left_frontal': [28, 24, 19], 'right_frontal': [4, 124, 117],
                        'left_parietal': [52, 53, 60], 'right_parietal': [85, 86, 92],
                        'occipital': [70, 75, 83]}
# sub_data = defaultdict(lambda : defaultdict(lambda: defaultdict(lambda: defaultdict)))
sub_data = {}
downsample_group = []

# Read in all the time series files
for f in os.listdir("/Users/margaretsheridan/Desktop/ts/"): 
	print "Starting on file: ", f
	subID = f[5:9]
	if subID not in sub_data:
		sub_data[subID] = {}
	condition = f[9:11]
	sub_data[subID][condition] = {}
	_, _, channel_array = get("/Users/margaretsheridan/Desktop/ts/" + f)

	# Downsample the ones sampled at 500 Hz
	if int(subID) <= 1037 and subID != '1018':
		signal = np.array([np.array([channel[i] for i in range(0,len(channel),2)]) for channel in channel_array])
	else:
		signal = channel_array

	for region in FOCUS_Electrodes:
		if region not in sub_data[subID][condition]:
			sub_data[subID][condition][region] = {}
		for channel_number in FOCUS_Electrodes[region]:
			sub_data[subID][condition][region][channel_number] = signal[channel_number - 1]

s = shelve.open("TS_DATA")
for sub in sub_data:
	s[sub] = sub_data[sub]
s.close()





