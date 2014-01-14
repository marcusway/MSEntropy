#! python
#
#  crossValidate_April2012.py
#  
#
#  Created by Bill Bosl on 4/09/12
#  Copyright (c) 2012 __Children's Hospital Boston__. All rights reserved.
#

import Orange
import orange
import orngTest, orngStat, orngFSS
import sys
import numpy as np


#--------------------------------------------------------------------
# Check command line arguments.
# The filename should be the second item given in the command line.
# If not, give a reminder of how to use this program, then  exit.
#--------------------------------------------------------------------
def check_command_line(argv, cl_keys):
    # Input flags:
    # -i inputfile
    # -o outputfile

    n_required_args = 1
    program_name = argv[0]
    argc = len(argv)
    nkeys = len(cl_keys)
    arg_check = 0
    nt_command = 0
    cl_arguments = {}

    for i in range(1, argc):
        for j in range(nkeys):
            if argv[i] == cl_keys[j]:
                cl_arguments[cl_keys[j]] = argv[i + 1]
                arg_check += 1

    if arg_check < n_required_args:
        print ""
        print "Only %d arguments given. Usage:" % (arg_check)
        print "   > python %s -i infilename -o outfilename -f nFeatures -t target" % (program_name)
        print "where only the -i argument is required. Exiting ..."
        print ""
        sys.exit()
    else:
        return cl_arguments

#============================================================================
# Read data from the given filename. 
# Data may be filtered after reading to reduce to a subset of the entire
# data set contained in the file.
#============================================================================


def getData(filename):
    data_read = Orange.orange.ExampleTable(filename)

    # These lines show how to filter out subjects from the dataset based on column header names and values
    # We'll skip this for now.
    #data_filtered = data_read.filter(Group=["epilepsy","control"])
    #data_filtered = data_read.filter({"Age":["12"],"Group":["con","hra"], "18m_raw_alg":(0,20)})

    # Don't filter out any of the data
    data_filtered = data_read

    return data_filtered

#============================================================================
# Main
#============================================================================
if __name__ == "__main__":

    #----------------------------------------------------
    # Check command line arguments
    #----------------------------------------------------
    c_line_keys = ["-i", "-o", "-f", "-t"]
    c_line_args = check_command_line(sys.argv, c_line_keys)

    #----------------------------------------------------
    # Some initializations: get the data, set target for
    # specificity and sensitivity calculations
    #----------------------------------------------------
    target = '1'
    #target = 'asd'
    kFolds = 20     # Number of subgroups for cross-validation
    nFeatures = 30                    # Default value

    #----------------------------------------------------
    # Parse the command line features. Note that we do
    # this after the default values have been assigned.
    #----------------------------------------------------
    if "-i" in c_line_args:
        filename = c_line_args["-i"]
        data = getData(filename)
    else:
        print "-i filename is required."
        exit()
    if "-f" in c_line_args:
        nFeatures = int(c_line_args["-f"])
    if "-t" in c_line_args:
        target = c_line_args["-t"]

    #----------------------------------------------------
    # Cross validation using Orange built-in methods
    #----------------------------------------------------

    # Set up all the potential learners
    bayes = Orange.classification.bayes.NaiveLearner(name='bayes')
    knn = Orange.classification.knn.kNNLearner(k=3, name='knn')
    tree = Orange.classification.tree.TreeLearner(min_instances=20, m_pruning=4, name='tree')
    forest = Orange.ensemble.forest.RandomForestLearner(trees=5, attributes=9, name="forest")
    bs = Orange.ensemble.boosting.BoostedLearner(tree, name="boosted tree")
    bg = Orange.ensemble.bagging.BaggedLearner(tree, name="bagged tree")
    svm = Orange.classification.svm.SVMLearnerEasy(name='svm')

    # You can test different learning methods alone or all at once
    # by adjusting the simple array of methods here. Orange contains
    # many more methods. In particular, SVM has several variations,
    # such as different basis functions. You can set up many of these
    # and include them here or not.
    learners = [knn, svm, bayes, tree, forest, bs, bg]

    # Carry out the cross validation calculations with all of the different learning methods
    results = Orange.evaluation.testing.cross_validation(learners, data, folds=kFolds)

    # Compute statistics on the results and print out
    cm = orngStat.computeConfusionMatrices(results, class_index=data.domain.classVar.values.index(target))
    ma = orngFSS.attMeasure(data)
    t0 = orngStat.CA(results)

    roc = orngStat.splitByIterations(results)
    #print "shape of roc = ", np.shape(roc)

    stat = (('CA', 'CA(results)'),
            ('Sens', 'sens(cm)'),
            ('Spec', 'spec(cm)'),
            ('AUC', 'AUC(results)'),
            ('IS', 'IS(results)'),
            ('Brier', 'BrierScore(results)'))

    #----------------------------------------------------------------------------------------
    # Perform a permutation analysis to compute an empirical p-value. The
    # method implemented here is described in detail in:
    #
    #   Golland, P., and Fischl, B. (2003). Permutation tests for classification: towards
    #   statistical significance in image-based studies. Inf Process Med Imaging 18, 330-341.
    #----------------------------------------------------------------------------------------

    # Set this to 100 or more to do an empirical significance estimate.
    # When set to zero, the permutation tests are not performed. Be aware that for
    # each permutation, the complete cross validation calculation, for each learner,
    # is carried out. So this can take a while. Set nPermutations to zero to skip this.
    nPermutations = 0

    # Some arrays to hold values
    pvalue = np.zeros(len(t0))
    items = range(len(data))
    data_p = data

    # Just loop through randomly permuted labels ...
    for m in range(nPermutations):
        if m < nPermutations - 1:
            np.random.shuffle(items)

        for i in range(len(data)):
            j = items[i]
            data_p[i].setclass(data[j].getclass())
        results_p = orngTest.crossValidation(learners, data_p, folds=kFolds)
        cm = orngStat.computeConfusionMatrices(results_p, classIndex=data_p.domain.classVar.values.index(target))
        t = orngStat.CA(results_p)
        for p in range(len(learners)):
            if t[p] >= t0[p]:
                pvalue[p] += 1.0

    if nPermutations > 0:
        pvalue /= (nPermutations * 1.0)

    scores = [eval("orngStat." + s[1]) for s in stat] + [pvalue]

    # Write out the empirical p-values
    Headers = "Learner   " + "".join(["%-7s" % s[0] for s in stat]) + 'p-value'

    print ""
    print ">>>>>  Target = %s, N=%d <<<<< " % (target, len(data))
    print Headers
    for (i, l) in enumerate(learners):
        print "%-8s " % l.name + "".join(["%5.3f  " % s[i] for s in scores if s[i] is not None])

