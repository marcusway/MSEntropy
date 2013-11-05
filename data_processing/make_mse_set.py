# This script was just intended to make a new dictionary containing only 
# mse data by region (averaged across the 3 regional electrodes) for 
# each scale for each region for each subject.  The dictionary was
# then written to just_mse.csv to see how the ML classifiers would
# fare with only the (almost) raw mse data. 

regions = ['left_frontal', 'right_frontal', 'left_parietal', 'right_parietal', 'occipital']
conditions = ['eo', 'ec']

new_dict = {}
for sub in F:
    new_dict[sub] = {}
    for condition in ['eo', 'ec']:
        if condition in F[sub]:
            for region in regions:
                for scale in range(20):
                    new_dict[sub][region + condition + str(scale)] = F[sub][condition][region]['mse'][scale]