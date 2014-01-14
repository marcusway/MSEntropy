import cPickle as pickle
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stat
import distill_mse

all_channels = range(129)

eo_dict = pickle.load(open("mse_eo_dict.p", "rb"))
ec_dict = pickle.load(open("mse_ec_dict.p", "rb"))
matched = pickle.load(open("Age_matched_focus_dict.p", "rb"))

inner = [7, 6, 106, 55, 12, 5, 29, 30, 31, 112, 105, 80, 54, 79, 62]
outer = [128, 48, 49, 56, 63, 68, 73, 81, 88, 94, 99, 107, 113, 119, 125]

inner_electrodes = [i - 1 for i in inner]
outer_electrodes = [i - 1 for i in outer]

for sub in matched:
    if 'eo' in matched[sub]:
        eo_outer_entropy = np.mean(
            [eo_dict[sub][electrode] for electrode in outer_electrodes], 0)
        eo_inner_entropy = np.mean(
            [eo_dict[sub][electrode] for electrode in inner_electrodes], 0)

        matched[sub]['eo']['outer'] = {}
        matched[sub]['eo']['inner'] = {}

        matched[sub]['eo']['outer']['mse'] = eo_outer_entropy
        matched[sub]['eo']['inner']['mse'] = eo_inner_entropy

        matched[sub]['eo']['outer']['coeffs'] = distill_mse.fit(eo_outer_entropy)
        matched[sub]['eo']['inner']['coeffs'] = distill_mse.fit(eo_inner_entropy)
    if 'ec' in matched[sub]:
        ec_outer_entropy = np.mean(
            [ec_dict[sub][electrode] for electrode in outer_electrodes], 0)
        ec_inner_entropy = np.mean(
            [ec_dict[sub][electrode] for electrode in inner_electrodes], 0)

        matched[sub]['ec']['outer'] = {}
        matched[sub]['ec']['inner'] = {}

        matched[sub]['ec']['outer']['mse'] = ec_outer_entropy
        matched[sub]['ec']['inner']['mse'] = ec_inner_entropy

        matched[sub]['ec']['outer']['coeffs'] = distill_mse.fit(ec_outer_entropy)
        matched[sub]['ec']['inner']['coeffs'] = distill_mse.fit(ec_inner_entropy)
