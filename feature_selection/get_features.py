# A nifty little script to do everything. 

# Import things
import cPickle as pickle
import csv
import distill_mse
import numpy as np


def make_sub_dict():
# Load all of the raw data:
    """


    :return:
    """
    with open('../Data/preliminary_042213/', 'rb') as ec:
        with open('../Data/sorted_mse_eo.p', 'rb') as eo:
            ec_dict, eo_dict = pickle.load(ec), pickle.load(eo)

            FOCUS_electrodes = {'left_frontal': [28, 24, 19], 'right_frontal': [4, 124, 117],
                                'left_parietal': [52, 53, 60], 'right_parietal': [85, 86, 92],
                                'occipital': [70, 75, 83]}

            all_subs = set(eo_dict.keys()).union(set(ec_dict.keys()))
            big_dict = {}

            # Just get the FOCUS regions and average across the electrodes
            for sub in all_subs:
                big_dict[sub] = {'eo': {}, 'ec': {}, 'Dx': None}
                if sub in eo_dict:
                    for region in FOCUS_electrodes:
                        big_dict[sub]['eo'][region] = np.mean(
                            np.array([eo_dict[sub][channel - 1] for channel in FOCUS_electrodes[region]]), 0)
                if sub in ec_dict:
                    for region in FOCUS_electrodes:
                        big_dict[sub]['ec'][region] = np.mean(
                            np.array([ec_dict[sub][channel - 1] for channel in FOCUS_electrodes[region]]), 0)

            # Add Dx to each subject
            with open('../Data/MASTER_DX_FILE_021513.csv', 'rU') as f:
                reader = csv.DictReader(f)

                for subject in reader:
                    if subject['sID'] in big_dict:
                        big_dict[subject['sID']]['Dx'] = subject['FINAL_DX']

                return big_dict


def max_test(big_dict):
    import scipy.stats

    # want to do a t-test comparing the maximum entropy at each region in each condition
    # so there will be ten t-tests here:  2 conditions x 5 regions

    # For each subject \\ For each condition \\ For each region:  compare average maximum.
    FOCUS_electrodes = dict(left_frontal=[28, 24, 19], right_frontal=[4, 124, 117],
                            left_parietal=[52, 53, 60], right_parietal=[85, 86, 92],
                            occipital=[70, 75, 83])

    print 'MAX ENTROPY COMPARISON\n'
    print "Region\tCondition\tt-statistic\tp-value\tequal_var"
    for condition in ['eo', 'ec']:
        for region in FOCUS_electrodes:
            ADHD_maxes = [max(big_dict[subject][condition][region]['mse']) for subject in big_dict if
                          big_dict[subject]['Dx'] == 'ADHD' if condition in big_dict[subject]]
            control_maxes = [max(big_dict[subject][condition][region]['mse']) for subject in big_dict if
                             big_dict[subject]['Dx'] == 'CONTROL' if condition in big_dict[subject]]

            # print ADHD_maxes
            # print control_maxes
            t, prob = scipy.stats.ttest_ind(ADHD_maxes, control_maxes)
            T, PROB = scipy.stats.bartlett(ADHD_maxes, control_maxes)
            print region, "\t", condition, "\t", t, "\t", prob, "\t", PROB > 0.05


def mean_test(big_dict):
    import scipy.stats

    # want to do a t-test comparing the maximum entropy at each region in each condition
    # so there will be ten t-tests here:  2 conditions x 5 regions

    # For each subject \\ For each condition \\ For each region:  compare average maximum.
    FOCUS_electrodes = dict(left_frontal=[28, 24, 19], right_frontal=[4, 124, 117],
                            left_parietal=[52, 53, 60], right_parietal=[85, 86, 92],
                            occipital=[70, 75, 83])

    print 'MEAN ENTROPY COMPARISON\n'

    print "Region\tCondition\tt-statistic\tp-value\tequal_var"
    for condition in ['eo', 'ec']:
        for region in FOCUS_electrodes:
            ADHD_means = [np.mean(big_dict[subject][condition][region]['mse']) for subject in big_dict if
                          big_dict[subject]['Dx'] == 'ADHD' if condition in big_dict[subject]]
            control_means = [np.mean(big_dict[subject][condition][region]['mse']) for subject in big_dict if
                             big_dict[subject]['Dx'] == 'CONTROL' if condition in big_dict[subject]]
            t, prob = scipy.stats.ttest_ind(ADHD_means, control_means)
            T, PROB = scipy.stats.bartlett(ADHD_means, control_means)
            print region, "\t", condition, "\t", t, "\t", prob, "\t", PROB > 0.05


def early_eo_vs_ec(big_dict):
    import scipy.stats

    # want to do a t-test comparing the maximum entropy at each region in each condition
    # so there will be ten t-tests here:  2 conditions x 5 regions

    # For each subject \\ For each condition \\ For each region:  compare average maximum.
    FOCUS_electrodes = dict(left_frontal=[28, 24, 19], right_frontal=[4, 124, 117],
                            left_parietal=[52, 53, 60], right_parietal=[85, 86, 92],
                            occipital=[70, 75, 83])

    print 'EO/EC EARLY DIFFERENCE COMPARISON\n'

    print "Region\tt-statistic\tp-value\tequal_var"
    for region in FOCUS_electrodes:
        ADHD_means = [np.mean(big_dict[subject]['eo'][region]['mse'][:6] - big_dict[subject]['ec'][region]['mse'][:6]) for subject in
                      big_dict if
                      big_dict[subject]['Dx'] == 'ADHD' and 'eo' in big_dict[subject] and 'ec' in big_dict[subject]]
        control_means = [np.mean(big_dict[subject]['eo'][region]['mse'][:6] - big_dict[subject]['ec'][region]['mse'][:6]) for subject
                         in big_dict if
                         big_dict[subject]['Dx'] == 'CONTROL' and 'eo' in big_dict[subject] and 'ec' in big_dict[subject]]
        t, prob = scipy.stats.ttest_ind(ADHD_means, control_means)
        T, PROB = scipy.stats.bartlett(ADHD_means, control_means)
        print region, "\t", t, "\t", prob, "\t", PROB > 0.05


def late_eo_vs_ec(big_dict):
    import scipy.stats

    # want to do a t-test comparing the maximum entropy at each region in each condition
    # so there will be ten t-tests here:  2 conditions x 5 regions

    # For each subject \\ For each condition \\ For each region:  compare average maximum.
    FOCUS_electrodes = dict(left_frontal=[28, 24, 19], right_frontal=[4, 124, 117],
                            left_parietal=[52, 53, 60], right_parietal=[85, 86, 92],
                            occipital=[70, 75, 83])

    print 'EO/EC LATE DIFFERENCE COMPARISON\n'

    print "Region\tt-statistic\tp-value\tequal_var"
    for region in FOCUS_electrodes:
        ADHD_means = [np.mean(big_dict[subject]['eo'][region]['mse'][6:] - big_dict[subject]['ec'][region]['mse'][6:]) for subject in
                      big_dict if
                      big_dict[subject]['Dx'] == 'ADHD' and 'eo' in big_dict[subject] and 'ec' in big_dict[subject]]
        control_means = [np.mean(big_dict[subject]['eo'][region]['mse'][6:] - big_dict[subject]['ec'][region]['mse'][6:]) for subject
                         in big_dict if
                         big_dict[subject]['Dx'] == 'CONTROL' and 'eo' in big_dict[subject] and 'ec' in big_dict[subject]]
        t, prob = scipy.stats.ttest_ind(ADHD_means, control_means)
        T, PROB = scipy.stats.bartlett(ADHD_means, control_means)
        print region, "\t", t, "\t", prob, "\t", PROB > 0.05


def overall_eo_vs_ec(big_dict):
    import scipy.stats

    # want to do a t-test comparing the maximum entropy at each region in each condition
    # so there will be ten t-tests here:  2 conditions x 5 regions

    # For each subject \\ For each condition \\ For each region:  compare average maximum.
    FOCUS_electrodes = dict(left_frontal=[28, 24, 19], right_frontal=[4, 124, 117],
                            left_parietal=[52, 53, 60], right_parietal=[85, 86, 92],
                            occipital=[70, 75, 83])

    print 'OVERALL EO VS EC\n'

    print "Region\tt-statistic\tp-value\tequal_var"
    for region in FOCUS_electrodes:
        ADHD_means = [np.mean(big_dict[subject]['eo'][region]['mse'] - big_dict[subject]['ec'][region]['mse']) for subject in big_dict
                      if big_dict[subject]['Dx'] == 'ADHD' and 'eo' in big_dict[subject] and 'ec' in big_dict[subject]]
        control_means = [np.mean(big_dict[subject]['eo'][region]['mse'] - big_dict[subject]['ec'][region]['mse']) for subject in
                         big_dict if
                         big_dict[subject]['Dx'] == 'CONTROL' and 'eo' in big_dict[subject] and 'ec' in big_dict[subject]]
        t, prob = scipy.stats.ttest_ind(ADHD_means, control_means)
        T, PROB = scipy.stats.bartlett(ADHD_means, control_means)
        print region, "\t", t, "\t", prob, "\t", PROB > 0.05


def curve_comparison(big_dict):
    import distill_mse
    import scipy.stats


    FOCUS_electrodes = dict(left_frontal=[28, 24, 19], right_frontal=[4, 124, 117],
                            left_parietal=[52, 53, 60], right_parietal=[85, 86, 92],
                            occipital=[70, 75, 83])
    curve_dict = {}
    for subject in big_dict:
        curve_dict[subject] = {}
        for condition in ['eo', 'ec']:
            curve_dict[subject][condition] = {}
            for region in FOCUS_electrodes:
                if condition in big_dict[subject]:
                    curve_dict[subject][condition][region] = distill_mse.fit(big_dict[subject][condition][region]['mse'], 4)

    print 'POLYNOMIAL COEFFICIENT COMPARISON\n'
    print "Region\tCondition\tCoeff\tt-statistic\tp-value\tequal_var"

    for region in FOCUS_electrodes:
        for condition in ['eo', 'ec']:
            for i in range(4):
                ADHD_coeffs = [curve_dict[subject][condition][region][i] for subject in big_dict if
                               big_dict[subject]['Dx'] == 'ADHD' if condition in big_dict[subject]]
                control_coeffs = [curve_dict[subject][condition][region][i] for subject in big_dict if
                                  big_dict[subject]['Dx'] == 'CONTROL' if condition in big_dict[subject]]
                T, PROB = scipy.stats.bartlett(ADHD_coeffs, control_coeffs)
                t, prob = scipy.stats.ttest_ind(ADHD_coeffs, control_coeffs)
                print region, "\t", condition, "\t", i, "\t", t, "\t", prob, "\t", PROB > 0.05


import cPickle as pickle
with open("../Data/preliminary_042213/AgeMatchedDict.p","r") as f:
    sub_dict = pickle.load(f)
    for function in [max_test, mean_test, early_eo_vs_ec, late_eo_vs_ec, overall_eo_vs_ec, curve_comparison]:
        function(sub_dict)
        print "\n"


