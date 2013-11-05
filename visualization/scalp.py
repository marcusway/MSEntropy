#!/Library/Frameworks/Python.framework/Versions/2.6/bin/python
#
#  scalp.py
#  
#
#  Created by William Bosl on 02/10/2010.
#  Copyright (c) 2009 Ingrain, Inc.. All rights reserved.
#
from numpy import *
import sys
import string
import glob
import scipy
import numpy as np
import matplotlib.pyplot as plt
#from matplotlib.pylab import *
from matplotlib.patches import Ellipse
from matplotlib.mlab import griddata
import itertools
#import MindLight

class scalpDisplay:
    """ Takes an array of 14, 19, 64 or 128 numbers and displays as a 2D scalp projection. """

    # Class variables go here
    coords = {}
    extendedData = []
    coordList = []
    colorlimits = [0.0, 1.0]
    mask_range = [-99999999999999.0, -99999999999999.0] # By default, avoid masking any values
    mask_color = 'w'
    mask = []

    ###############################################################################################################################
    # Coordinates for  14, 19, 64 (default) or 128 electrodes are specified here. You can also use a file containing coordinates
    # with the format: "name" x y z, where "name" is the electrode name or number. Note that each of the sets below contain
    # more than 64/128 electrodes, including reference, ear and so forth. Currently, in the 64 electrode set these values
    # are simply set to the average of nearby points in order to make the display look smooth and continuous. See fillChannels().
    ###############################################################################################################################

    #================================================
    #================================================
    def setMask(self, range, color, mask):
        self.mask_range = range
        self.mask_color = color
        self.mask = mask

    #================================================
    # The Emotiv system uses 14 electrodes.
    #================================================
    #	def __init__(self):
    def define14Electrodes(self):
        self.coords = {1: [5.0, 10.5, 0.0], 2: [-5.0, 10.5, 0.0],
                       3: [-6.8, 4.5, 0.0], 4: [-11.6, 7.6, 0.0], 5: [-10.5, -0.9, 0.0],
                       6: [-10.7, -8.6, 0.0], 7: [-5.0, -13.0, 0.0],
                       8: [5.0, -13.0, 0.0], 9: [10.7, -8.6, 0.0],
                       10: [10.5, -0.9, 0.0],
                       11: [6.8, 4.5, 0.0], 12: [11.6, 7.6, 0.0],
                       13: [7.2, 15.0, 0.0], 14: [-7.2, 15.0, 0.0],
                       "nose": [0.0, 15.0, 0.0], "back": [0.0, -15.0, 0.0]}

    #		"REF":[0.0, 0.0, 0.0],"COM":[9.8, -13.0, 0.0],"LeftEar1":[-16.0, -0.8, 0.0],
    #		62:[5.2, 7.0, 0.0],"LeftEar2":[-13.8, 1.2, 0.0],"RightEar1":[16.0, -0.8, 0.0],"RightEar2":[13.8, 1.2, 0.0]}

    #================================================
    # Standard 10-20 system
    #================================================
    def define19Electrodes(self):
        self.coords = {
            "Fp1": [-2.70, 8.88, 1.09], "Fp2": [2.70, 8.88, 1.09],
            "F7": [-6.40, 4.13, -0.36], "F3": [-4.46, 6.02, 4.37], "Fz": [0.00, 7.96, 5.04], "F4": [4.46, 6.02, 4.37],
            "F8": [6.40, 4.13, -0.36],
            "T7": [-7.30, -1.87, -0.63], "C3": [-5.48, 0.28, 6.38], "Cz": [0.00, 0.00, 8.90], "C4": [5.48, 0.28, 6.38],
            "T8": [7.30, -1.87, -0.63],
            "P7": [-6.03, -5.76, 0.05], "P3": [-5.83, -4.49, 4.96], "Pz": [0.00, -6.68, 6.47],
            "P4": [5.83, -4.49, 4.96],
            "P8": [6.03, -5.76, 0.05],
            "O1": [-2.74, -8.61, 0.24], "O2": [2.74, -8.61, 0.24]
        }

        self.coords = [[-5.48, 0.28, 6.38], [5.48, 0.28, 6.38], [-2.74, -8.61, 0.24], [2.74, -8.61, 0.24],
                       [0.00, 0.00, 8.90], [-4.46, 6.02, 4.37], [4.46, 6.02, 4.37], [-6.40, 4.13, -0.36],
                       [6.40, 4.13, -0.36],
                       [0.00, 7.96, 5.04], [-2.70, 8.88, 1.09], [2.70, 8.88, 1.09], [-5.83, -4.49, 4.96],
                       [5.83, -4.49, 4.96],
                       [0.00, -6.68, 6.47], [-7.30, -1.87, -0.63], [7.30, -1.87, -0.63], [-6.03, -5.76, 0.05],
                       [6.03, -5.76, 0.05]
        ]

    # Channel ordering expected for these coordinates: ["C3","C4","O1","O2","Cz","F3","F4","F7","F8","Fz","Fp1","Fp2","P3","P4","Pz","T7","T8","P7","P8"]
    # Old names T3, T5, T4 and T6 --> New names T7, P7, T8, and P8


    #================================================
    #================================================
    def define64Electrodes(self):
        self.coords = {1: [8.8, 11.4, 0.0], 2: [5.0, 10.5, 0.0], 3: [1.9, 8.0, 0.0], 4: [0.0, 5.6, 0.0],
                       5: [-1.5, 2.0, 0.0], 6: (3.9, 13.7, 0.0),
                       7: [0.0, 11.5, 0.0], 8: [-1.9, 8.0, 0.0], 9: [-2.9, 4.8, 0.0], 10: [0.0, 16.5, 0.0],
                       11: [-3.9, 13.7, 0.0], 12: [-5.0, 10.5, 0.0], 13: [-5.2, 7.0, 0.0],
                       14: [-8.8, 11.4, 0.0], 15: [-8.2, 8.0, 0.0], 16: [-6.8, 4.5, 0.0], 17: [-5.0, 2.0, 0.0],
                       18: [-2.8, -1.0, 0.0], 19: [-11.6, 7.6, 0.0],
                       20: [-11.0, 3.6, 0.0], 21: [-8.0, 0.9, 0.0], 22: [-5.4, -1.8, 0.0], 23: [-15.3, 5.5, 0.0],
                       24: [-10.5, -0.9, 0.0], 25: [-8.0, -2.5, 0.0],
                       26: [-13.4, -3.5, 0.0], 27: [-10.0, -5.3, 0.0], 28: [-6.4, -5.5, 0.0], 29: [-3.1, -4.0, 0.0],
                       30: [0.0, -2.5, 0.0], 31: [-10.7, -8.6, 0.0],
                       32: [-6.6, -9.5, 0.0], 33: [-3.6, -7.2, 0.0], 34: [0.0, -5.6, 0.0], 35: [-9.8, -13.0, 0.0],
                       36: [-5.0, -13.0, 0.0], 37: [-2.6, -11.2, 0.0],
                       38: [0.0, -8.5, 0.0], 39: [0.0, -14.0, 0.0], 40: [2.6, -11.2, 0.0], 41: [3.6, -7.2, 0.0],
                       42: [3.1, -4.0, 0.0], 43: [2.8, -1.0, 0.0],
                       44: [5.0, -13.0, 0.0], 45: [6.6, -9.5, 0.0], 46: [6.4, -5.5, 0.0], 47: [5.4, -1.8, 0.0],
                       48: [10.7, -8.6, 0.0], 49: [10.0, -5.3, 0.0],
                       50: [8.0, -2.5, 0.0], 51: [13.4, -3.5, 0.0], 52: [10.5, -0.9, 0.0], 53: [8.0, 0.9, 0.0],
                       54: [5.0, 2.0, 0.0], 55: [1.5, 2.0, 0.0],
                       56: [11.0, 3.6, 0.0], 57: [6.8, 4.5, 0.0], 58: [2.9, 4.8, 0.0], 59: [15.3, 5.5, 0.0],
                       60: [11.6, 7.6, 0.0], 61: [8.2, 8.0, 0.0],
                       63: [7.2, 15.0, 0.0], 64: [-7.2, 15.0, 0.0], "REF": [0.0, 0.0, 0.0], "COM": [9.8, -13.0, 0.0],
                       "LeftEar1": [-16.0, -0.8, 0.0],
                       62: [5.2, 7.0, 0.0], "LeftEar2": [-13.8, 1.2, 0.0], "RightEar1": [16.0, -0.8, 0.0],
                       "RightEar2": [13.8, 1.2, 0.0]}

    #================================================
    #================================================
    def define128Electrodes(self):
        self.coords = {"FidNz": [0.00, 9.07, -2.36], "FidT9": [-6.71, 0.04, -3.25], "FidT10": [6.71, 0.04, -3.25],
                       "E1": [5.79, 5.52, -2.58], "E2": [5.29, 6.71, 0.31],
                       "E3": [3.86, 7.63, 3.07], "E4": [2.87, 7.15, 4.99], "E5": [1.48, 5.69, 6.81],
                       "E6": [0.00, 3.81, 7.89], "E7": [-1.22, 1.56, 8.44], "E8": [4.22, 8.00, -1.35],
                       "E9": [2.70, 8.88, 1.09], "E10": [1.83, 8.71, 3.19], "E11": [0.00, 7.96, 5.04],
                       "E12": [-1.48, 5.69, 6.81], "E13": [-2.44, 3.25, 7.61], "E14": [1.27, 9.48, -0.95],
                       "E15": [0.00, 9.09, 1.33], "E16": [0.00, 9.08, 3.11], "E17": [0.00, 9.27, -2.21],
                       "E18": [-1.83, 8.71, 3.19], "E19": [-2.87, 7.15, 4.99], "E20": [-3.83, 5.12, 5.94],
                       "E21": [-1.27, 9.48, -0.95], "E22": [-2.70, 8.88, 1.09], "E23": [-3.86, 7.63, 3.07],
                       "E24": [-4.46, 6.02, 4.37], "E25": [-4.22, 8.00, -1.35], "E26": [-5.29, 6.71, 0.31],
                       "E27": [-5.68, 5.45, 2.84], "E28": [-5.55, 4.16, 4.63], "E29": [-4.76, 2.70, 6.30],
                       "E30": [-3.70, 0.96, 7.63], "E31": [-1.96, -0.68, 8.56], "E32": [-5.79, 5.52, -2.58],
                       "E33": [-6.40, 4.13, -0.36], "E34": [-6.82, 2.97, 2.43], "E35": [-6.41, 1.49, 4.74],
                       "E36": [-5.48, 0.28, 6.38], "E37": [-3.91, -1.52, 7.76], "E38": [-6.55, 3.61, -3.35],
                       "E39": [-7.19, 0.85, -0.88], "E40": [-7.39, 0.03, 2.14], "E41": [-6.91, -0.80, 4.60],
                       "E42": [-5.96, -2.34, 6.00], "E43": [-6.52, 2.42, -5.25], "E44": [-6.84, 1.28, -3.56],
                       "E45": [-7.30, -1.87, -0.63], "E46": [-7.31, -2.30, 2.39], "E47": [-6.74, -3.01, 4.18],
                       "E48": [-5.93, 2.23, -7.93], "E49": [-6.30, 0.42, -6.07], "E50": [-6.78, -4.02, -0.23],
                       "E51": [-6.56, -4.67, 2.75], "E52": [-5.83, -4.49, 4.96], "E53": [-4.19, -4.04, 6.98],
                       "E54": [-2.27, -3.41, 8.20], "E55": [0.00, -2.14, 8.79], "E56": [-6.17, -2.46, -5.64],
                       "E57": [-6.58, -3.74, -2.99], "E58": [-6.03, -5.76, 0.05], "E59": [-5.20, -6.44, 2.98],
                       "E60": [-4.12, -6.06, 5.37], "E61": [-2.34, -5.48, 7.06], "E62": [0.00, -6.68, 6.47],
                       "E63": [-5.33, -4.30, -5.61], "E64": [-5.40, -5.87, -2.89], "E65": [-4.65, -7.28, 0.13],
                       "E66": [-3.61, -7.67, 3.13], "E67": [-1.84, -7.35, 5.22], "E68": [-3.78, -6.40, -5.26],
                       "E69": [-3.53, -7.60, -2.82], "E70": [-2.74, -8.61, 0.24], "E71": [-1.40, -8.44, 3.28],
                       "E72": [0.00, -7.83, 4.69], "E73": [-1.93, -7.50, -5.14], "E74": [-1.13, -8.46, -2.63],
                       "E75": [0.00, -9.00, 0.49], "E76": [1.40, -8.44, 3.28], "E77": [1.84, -7.35, 5.22],
                       "E78": [2.34, -5.48, 7.06], "E79": [2.27, -3.41, 8.20], "E80": [1.96, -0.68, 8.56],
                       "E81": [0.00, -7.86, -4.95], "E82": [1.13, -8.46, -2.63], "E83": [2.74, -8.61, 0.24],
                       "E84": [3.61, -7.67, 3.13], "E85": [4.12, -6.06, 5.37], "E86": [4.19, -4.04, 6.98],
                       "E87": [3.91, -1.52, 7.76], "E88": [1.93, -7.50, -5.14], "E89": [3.53, -7.60, -2.82],
                       "E90": [4.65, -7.28, 0.13], "E91": [5.20, -6.44, 2.98], "E92": [5.83, -4.49, 4.96],
                       "E93": [5.96, -2.34, 6.00], "E94": [3.78, -6.40, -5.26], "E95": [5.40, -5.87, -2.89],
                       "E96": [6.03, -5.76, 0.05], "E97": [6.56, -4.67, 2.75], "E98": [6.74, -3.01, 4.18],
                       "E99": [5.33, -4.30, -5.61], "E100": [6.58, -3.74, -2.99], "E101": [6.78, -4.02, -0.23],
                       "E102": [7.31, -2.30, 2.39], "E103": [6.91, -0.80, 4.60], "E104": [5.48, 0.28, 6.38],
                       "E105": [3.70, 0.96, 7.63], "E106": [1.22, 1.56, 8.44], "E107": [6.17, -2.46, -5.64],
                       "E108": [7.30, -1.87, -0.63], "E109": [7.39, 0.03, 2.14], "E110": [6.41, 1.49, 4.74],
                       "E111": [4.76, 2.70, 6.30], "E112": [2.44, 3.25, 7.61], "E113": [6.30, 0.42, -6.07],
                       "E114": [6.84, 1.28, -3.56], "E115": [7.19, 0.85, -0.88], "E116": [6.82, 2.97, 2.43],
                       "E117": [5.55, 4.16, 4.63], "E118": [3.83, 5.12, 5.94], "E119": [5.93, 2.23, -7.93],
                       "E120": [6.52, 2.42, -5.25], "E121": [6.55, 3.61, -3.35], "E122": [6.40, 4.13, -0.36],
                       "E123": [5.68, 5.45, 2.84], "E124": [4.46, 6.02, 4.37], "E125": [6.12, 4.52, -4.41],
                       "E126": [3.74, 6.65, -6.53], "E127": [-3.74, 6.65, -6.53], "E128": [-6.12, 4.52, -4.41],
                       "Cz": [0.00, 0.00, 8.90]}

    def setColorLimits(self, low, high):
        self.colorlimits = [low, high]

    #================================================
    #================================================
    def fillChannels(self, data):
        nChannels = len(data)
        self.extendedData = zeros(len(self.coords))

        for i in range(nChannels):
            self.extendedData[i] = data[i]

        if nChannels == 14:
        # nose
            self.extendedData[14] = (data[12] + data[13]) / 2.0
            # back
            self.extendedData[15] = (data[6] + data[7]) / 2.0

        if nChannels == 64:
            # REF
            self.extendedData[64] = (data[4] + data[54] + data[17] + data[29] + data[42]) / 5.0
            # COM
            self.extendedData[65] = (data[43] + data[47]) / 2.0
            # LeftEar1
            self.extendedData[66] = (data[19] + data[22] + data[23]) / 3.0
            # LeftEar2
            self.extendedData[67] = (self.extendedData[66] + data[23] + data[25]) / 3.0
            # RightEar1
            self.extendedData[68] = (data[51] + data[55] + data[58]) / 3.0
            # RightEar2
            self.extendedData[69] = (data[50] + self.extendedData[68] + data[58]) / 3.0

        if data[0] == 0.0: self.extendedData[0] = mean(self.extendedData)

    #================================================
    # I don't actually use this currently. But
    # it seems like a good idea to have.
    #================================================
    def getCoordsFromFile(self, filename):
        try:
            print "Get coords from file ", filename
            f = open(filename)
        except IOError:
            print "File \'", filename, "\' cannot be found. Returning ..."
            return
            # Parse the data
        self.coords = {}    # reset the coordinate dictionary
        allLines = f.readlines()
        nlines = len(allLines)
        for i in range(nlines):
            line = string.split(allLines[i])
            k = line[0]
            if k[0] == 'E':
                key = string.atoi(k[1:])
            else:
                key = k
            x = string.atof(line[1])
            y = string.atof(line[2])
            z = string.atof(line[3])
            self.coords[key] = [x, y, z]

    #================================================
    #================================================
    def displayScalpEEG(self, plt, data, title="", addLabels=True):

        #------------------------------------------------
        # Check: there must be more electrodes than data
        #------------------------------------------------
        colorlimits = self.colorlimits
        nChannels = len(data)
		if nChannels == 128:   self.define128Electrodes()
		elif nChannels == 64:  self.define64Electrodes()
		elif nChannels == 19:  self.define19Electrodes()
		elif nChannels == 14:  self.define14Electrodes()
		else:
			print "Data array must contain either 64 or 128 values; contains",len(data),"values."
			return
			
		#------------------------------------------------
		# Set up coordinate display map
		#------------------------------------------------
		nElectrodes = len(self.coords)
		xloc = zeros(nElectrodes)
		yloc = zeros(nElectrodes)
		zloc = zeros(nElectrodes)
		for i,c in enumerate(self.coords):
			#xloc[i] = self.coords[c][0]
			#yloc[i] = self.coords[c][1]
			#zloc[i] = self.coords[c][2]
			xloc[i] = self.coords[i][0]
			yloc[i] = self.coords[i][1]
			zloc[i] = self.coords[i][2]
			
		#------------------------------------------------
		# Get dimensions of the electrode array
		#------------------------------------------------
		minZ = min(zloc)
		maxZ = max(zloc)
		dz = maxZ-minZ
		if dz > 0.0:
			for i in range(len(xloc)):
				xloc[i] *= exp(-(zloc[i]-minZ)/dz)
				yloc[i] *= exp(-(zloc[i]-minZ)/dz)
		
		minX = min(xloc)
		maxX = max(xloc)
		dx = maxX-minX
		minY = min(yloc)
		maxY = max(yloc)
		dy = maxY-minY
		
		# First make the head circular
		if dx != dy:
			squishFactor = dy/dx
			for i in range(len(xloc)):
				xloc[i] *= squishFactor
			minX = min(xloc)
			maxX = max(xloc)
			dx = maxX-minX
		
		
		#------------------------------------------------
		# Electrodes that are close to the edge should
		# be moved out to the edge
		#------------------------------------------------
		HR = maxX # head radius
		maxChange = 0.0
		for i in range(len(xloc)):
			x = xloc[i]
			y = yloc[i]
			r = sqrt(x*x + y*y)
			if r/HR > 0.8: maxChange = HR/r
			
		for i in range(len(xloc)):
			x = xloc[i]
			y = yloc[i]
			r = sqrt(x*x + y*y)
			if r/HR > 0.85:
				theta = arctan2(y,x)
				xloc[i] = maxX * cos(theta)
				yloc[i] = maxY * sin(theta) 
			else:
				xloc[i] *= maxChange
				yloc[i] *= maxChange
		
		
		# To look right, the head should be slightly larger in the y-direction than in x
		squishFactor = 0.85
		for i in range(len(xloc)):
			xloc[i] *= squishFactor
		minX = min(xloc)
		maxX = max(xloc)
		minY = min(yloc)
		maxY = max(yloc)
		dx = maxX-minX
		
		#------------------------------------------------
		# Add entropy and the mean slope of the entropy curve. Flat lines are zero, rising are 
		# positive, decreasing are negative.
		#------------------------------------------------
			
		# Make a colormap for the data
		nc = len(data)
		sm = plt.cm.ScalarMappable()
		sm.set_array(data)
		sm.autoscale()
		dataColormap = sm.get_cmap()
		sm.set_clim(colorlimits)

		#------------------------------------------------
		# Create a 2D plot
		#------------------------------------------------
		gc = plt.gca()

		# Add a circle to outline the head
		cx = 0
		cy = 0
		head = Ellipse((cx,cy), width=2*maxX, height=2*maxY, fc='none')
		gc.add_patch(head)

		# Draw arrow for the nose
		cx=0
		cy=maxY
		w = maxX/20.0
		dx = 0
		dy = w/10.0
		nose = plt.arrow(cx,cy, dx, dy, linewidth=0.5, width=w,  color='k')
		gc.add_patch(nose)

		# Draw ellipses for ears
		w = maxX/10.0
		cx= maxX + w/2
		cy= 0
		ell = Ellipse((cx,cy), width=w, height=4*w, fc='k')
		gc.add_patch(ell)
		cx= -maxX - w/2
		ell = Ellipse((cx,cy), width=w, height=4*w, fc='k')
		gc.add_patch(ell)

		# define grid.
		xi = linspace(minX,maxX,400)
		yi = linspace(minY,maxY,400)

		# grid the data.
		self.fillChannels(data)
		zloc = scipy.random.random(shape(xloc))		
		zi = griddata(xloc,yloc,self.extendedData,xi,yi)		
		
		# contour the gridded data, plotting dots at the randomly spaced data points.
		CS = plt.contourf(xi,yi,zi,100,cmap=plt.cm.jet)
		
		# Set a mask for regions that where we don't want to show data
		if len(self.mask) > 0:
			self.fillChannels(self.mask)
			zloc = scipy.random.random(shape(xloc))		
			zi = griddata(xloc,yloc,self.extendedData,xi,yi)		
			CS = plt.contourf(xi,yi,zi,self.mask_range, colors=(self.mask_color)) 
		
		# Use this to set the maximum value on the color scale
		CS.set_clim(self.colorlimits) 
		
		# colorbar? 
		if addLabels:
			mn = self.colorlimits[0]
			mx = self.colorlimits[1]
			md = (mx-mn)/2
			mn = 0
			mx = 300
			v = np.linspace(mn, mx, 3, endpoint=True)
			
			cbar = plt.colorbar(ticks=v)
			cbar.set_ticks([mn,md,mx])
			cbar.set_ticklabels([mn,md,mx])
			
			#plt.colorbar() # draw colorbar
			
		width = 2
		height = width
		
		# plot data points.
		plt.scatter(xloc,yloc,marker='o',c='k',s=8)
		gc.set_xticklabels("")
		gc.set_yticklabels("")

		plt.title(title, fontsize=10)
#		plt.show()

		return CS
		

	#============================================================================
	# Main
	#============================================================================
	if __name__ == "__main__":
		import matplotlib.pyplot as plt
		
		argc = len(sys.argv)
		if argc < 2:
			print "Usage: python scalp.py file.data <coordinates.dat>"
			nChannels = 64
			data = scipy.random.random(nChannels)
			dfilename = "Test"
			cfilename = "none"
		if argc >= 2:
			dfilename = sys.argv[1]
			cfilename = "GSN-HydroCel-129.txt"
			
			# Check for existence
			try:
				dfile = open(dfilename)
				allLines = dfile.readlines()
				dfile.close()
			except IOError:
				print "File \'",dfilename,"\' cannot be found. Exiting ..."
				sys.exit()
			
			# Get the data
			nChannels = len(allLines)
			data = zeros(nChannels)
			for i in range(nChannels):
				data[i] = string.atof(allLines[i])
				
		# Create the scalp display instance and create the plot
		import scalp
		sc = scalp.scalpDisplay()	
		sc.setColorLimits(5,20)			
		sc.displayScalpEEG(plt, data, dfilename, True)
		plt.show()

		
