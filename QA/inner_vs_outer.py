# A script to test if the entropy is different between 
# the outer ring of electrodes, which are all marked 
# as being bad, and the inner electrodes (closest
# to the center)
import cPickle as pickle 
import matplotlib.pyplot as plt 
import numpy as np 
import scipy.stats as stat
import random
import time
all_channels = range(129)

inner = [7, 6, 106, 55, 12,5, 29, 30, 31, 112, 105, 80, 54, 79, 62]
outer = [128, 48, 49, 56, 63, 68, 73, 81, 88, 94, 99, 107, 113, 119, 125]

inner_electrodes = [i-1 for i in inner]
outer_electrodes = [i-1 for i in outer]
random.seed(time.time())
#inner_electrodes = [random.choice(all_channels) for i in range(15)]
#outer_electrodes = [random.choice(all_channels) for i in range(15)]


eo = pickle.load(open("mse_eo_dict.p","r"))
ec = pickle.load(open("mse_ec_dict.p","r"))
matched = pickle.load(open("matched.p","r"))

eo_outer_entropy = [np.mean([eo[sub][electrode] for electrode in range(129) if electrode in outer_electrodes],0) for sub in eo if sub in matched]
eo_inner_entropy = [np.mean([eo[sub][electrode] for electrode in range(129) if electrode in inner_electrodes],0) for sub in eo if sub in matched]

avg_eo_outer = np.mean(eo_outer_entropy,0)
avg_eo_inner = np.mean(eo_inner_entropy,0)

eo_outer_err = stat.sem(eo_outer_entropy, 0)
eo_inner_err = stat.sem(eo_inner_entropy, 0)

print "eo_outer_entropy has ", len(eo_outer_entropy), "entries, each of which has", len(eo_outer_entropy[0]), "entries"
print eo_outer_entropy
print "avg_eo_outer has ", len(avg_eo_outer), "entries"

plt.errorbar(range(1,21),avg_eo_outer, yerr=eo_outer_err, xerr=None, color="b")
plt.errorbar(range(1,21),avg_eo_inner, yerr=eo_inner_err, xerr=None, color="r")
plt.title("Eyes Open")
plt.ylabel("mSampEn")
plt.xlabel("Scale")
plt.legend(("Outer Electrodes", "Inner Electrodes"), loc=4)

plt.show()

ec_outer_entropy = [np.mean([ec[sub][electrode] for electrode in range(129) if electrode in outer_electrodes],0) for sub in ec if sub in matched]
ec_inner_entropy = [np.mean([ec[sub][electrode] for electrode in range(129) if electrode in inner_electrodes],0) for sub in ec if sub in matched]

avg_ec_outer = np.mean(ec_outer_entropy,0)
avg_ec_inner = np.mean(ec_inner_entropy,0)

ec_outer_err = stat.sem(ec_outer_entropy, 0)
ec_inner_err = stat.sem(ec_inner_entropy, 0)

plt.errorbar(range(1,21),avg_ec_outer, yerr=eo_outer_err, xerr=None, color="b")
plt.errorbar(range(1,21),avg_ec_inner, yerr=eo_inner_err, xerr=None, color="r")
plt.title("Eyes Closed")
plt.ylabel("mSampEn")
plt.xlabel("Scale")
plt.legend(("Outer Electrodes", "Inner Electrodes"), loc=4)

plt.show()