"""
This is a dumb script that I used that one time to compute a ridiculous number of features 
for all my EEG signals.
"""

import shelve
import cPickle as pickle

import numpy as np

import pyEEG

matched_subs = pickle.load(open("/Users/margaretsheridan/Desktop/LAB/FOCUS/EEG_Machine_Learning/MSE/Data/datasets/pickledData/matched.p", "rb"))

db = shelve.open("TS_DATA")
new_db = shelve.open("EEG_FEATURES")

# min_length = {'ec': 1000000, 'eo': 1000000}
# for sub in db:
#     if 'eo' in db[sub]:
#         min_length['eo'] = min(min_length['eo'], len(db[sub]['eo']['left_frontal'][28]))
#     if 'ec' in db[sub]:
#         min_length['ec'] = min(min_length['ec'], len(db[sub]['ec']['left_frontal'][28]))

# Perform pretty much all of the pyEEG procedures on each of the focus electrodes, and then 
# average across the focus electrodes to get a regional number. 

# band = [1, 4, 8, 13, 30]
# for sub in sub_data:

    # Execute these pyEEG functions:
    # bin_power(X, band, Fs)
    # first_order_diff(X)
    # hurst(X)
    # pfd(X)
    # hfd(X)
    # hjorth, X
    # spectral_entropy(X, Band, FS)
    # dfa(X)
    # fisher_info(X, Tau, DE)
    # svd_entropy(X, Tau, DE)

kmax = 5
tau = 4
band = [1, 5, 8, 12, 30]
Fs = 250

new = {}

for sub in matched_subs:
    print "Processing Subject:", sub
    new[sub] = {}
    for condition in db[sub]:
        new[sub][condition] = {}
        for region in db[sub][condition]:
            new[sub][condition][region] = {}
            bin_power = []
            pfd = []
            hfd = []
            hjorth_mob = []
            hjorth_comp = []
            spectral_entropy = []
            svd_entropy = []
            fisher_info = []
            dfa = []
            bin_power_ratio = []

            for channel in db[sub][condition][region]:
                X = db[sub][condition][region][channel]#[:min_length[condition]]
                first_order_diff = np.diff(X)
                power, Power_Ratio = pyEEG.bin_power(X, band, Fs)
                bin_power.append(power)
                bin_power_ratio.append(Power_Ratio)
                #print "Bin power:", bin_power
                pfd.append(pyEEG.pfd(X, D=first_order_diff))
                #print "pfd = ", pfd
                hfd.append(pyEEG.hfd(X, kmax))
                #print "hfd=", hfd
                hjorth_mobility, hjorth_complexity = pyEEG.hjorth(X, D=list(first_order_diff))
                hjorth_mob.append(hjorth_mobility)
                hjorth_comp.append(hjorth_complexity)
                #print "hjorth = ", hjorth
                spectral_entropy.append(pyEEG.spectral_entropy(X, band, Fs, Power_Ratio=Power_Ratio))
                #print "spectral_entropy = ", spectral_entropy
                svd_entropy.append(pyEEG.svd_entropy(X, 2, 20))
                #print "svd_entropy = ", svd_entropy
                fisher_info.append(pyEEG.fisher_info(X, 4, 10))
                #print "fisher info = ", fisher_info
                dfa.append(pyEEG.dfa(X))

            mean_bin_power = np.mean(bin_power, axis=0)
            mean_rel_power = np.mean(bin_power_ratio, axis=0)
            new[sub][condition][region]['Relative Delta'] = mean_rel_power[0]
            new[sub][condition][region]['Absolute Delta'] = mean_bin_power[0]
            new[sub][condition][region]['Relative Theta'] = mean_rel_power[1]
            new[sub][condition][region]['Absolute Theta'] = mean_bin_power[1]            
            new[sub][condition][region]['Relative Alpha'] = mean_rel_power[2]
            new[sub][condition][region]['Absolute Alpha'] = mean_bin_power[2]
            new[sub][condition][region]['Relative Beta'] = mean_rel_power[3]
            new[sub][condition][region]['Absolute Beta'] = mean_bin_power[3]
            
            new[sub][condition][region]["Petrosian Fractal Density"] = np.mean(pfd)
            new[sub][condition][region]["Higuchi Fractal Dimension"] = np.mean(hfd)
            new[sub][condition][region]["Spectral Entropy"] = np.mean(spectral_entropy)
            new[sub][condition][region]["SVD Entropy"] = np.mean(svd_entropy)
            new[sub][condition][region]["Fisher Info"] = np.mean(fisher_info)
            new[sub][condition][region]["Hjorth Mobility"] = np.mean(hjorth_mob)
            new[sub][condition][region]["Hjorth Complexity"] = np.mean(hjorth_comp)

            

for sub in new:
    new_db[sub] = new[sub]
new_db.close()
db.close()





