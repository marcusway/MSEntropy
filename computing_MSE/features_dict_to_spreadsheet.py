"""
Right now, we have a dictionary that is pretty nested: 
    db[sub][condition][region][feature]
"""
import csv
import shelve
import cPickle as pickle

import flatten

db = shelve.open("EEG_FEATURES")
new_db = shelve.open("FLATTENED_FEATURES_DICT_NON_TRUNCATED")
new_dict = {}

matched = pickle.load(open("../../Data/datasets/pickledData/AgeMatchedDict.p"))

for sub in db:
    new_dict[sub] = {" ".join(x):y for x,y in flatten.flattenDict(db[sub]).items()}
    new_dict[sub]['Dx'] = matched[sub]['Dx']
out = open("features_non_truncated.csv","w")

writer = csv.DictWriter(out, [key for key in 
    new_dict['1109'].keys() if key != 'Dx'] + ['Dx'])

writer.writeheader()

for sub in new_dict:
    new_db[sub] = new_dict[sub]
    writer.writerow(new_dict[sub])

new_db.close()
db.close()







