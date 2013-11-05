def print_mse_data():
    """
    This was just used to generate a spreadsheet
    of MSE data whose format was later changed
    to a more reasonable one.  This may be useful,
    but I don't really know. 

    """
    import cPickle as pickle
    import csv
    import numpy as np
    import distill_mse
    # Load all of the raw data:
    with open('../Data/sorted_mse_ec.p', 'rb') as ec:
        with open('../Data/sorted_mse_eo.p', 'rb') as eo:

            #----------------------
            # Get average mse curves for FOCUS regions
            #----------------------

            ec_dict, eo_dict = pickle.load(ec), pickle.load(eo)

            FOCUS_electrodes = dict(left_frontal=[28, 24, 19], right_frontal=[4, 124, 117],
                                    left_parietal=[52, 53, 60], right_parietal=[85, 86, 92],
                                    occipital=[70, 75, 83])

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

            #--------------------
            # Add Dx to each subject
            #---------------------

            with open('../Data/MASTER_DX_FILE_021513.csv', 'rU') as f:
                reader = csv.DictReader(f)

                print 'Subject\tAge\tSex\tCondition\tRegion\tCoeff1\tCoeff2\tCoeff3\tCoeff4\tCoeff5\tMax\tMean'

                for subject in reader:
                    if subject['sID'] in big_dict:
                        big_dict[subject['sID']]['Dx'] = subject['FINAL_DX']
                        big_dict[subject['sID']]['sex'] = subject['sex']
                        big_dict[subject['sID']]['age'] = subject['age']
                for subject in big_dict:
                    for condition in ['eo', 'ec']:
                        if big_dict[subject][condition]:
                            for region in FOCUS_electrodes:
                                max_entropy = max(big_dict[subject][condition][region])
                                mean_entropy = np.mean(big_dict[subject][condition][region])
                                curve = distill_mse.fit(big_dict[subject][condition][region], 4)

                                print '\t'.join(map(str, [subject, big_dict[subject]['age'], big_dict[subject]['sex'],
                                                          condition, region, curve[0], curve[1], curve[2], curve[3],
                                                          curve[4], max_entropy, mean_entropy]))

if __name__ == "__main__":
    print_mse_data()


