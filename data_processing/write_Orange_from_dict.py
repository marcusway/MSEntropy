# Hopefully this works to take a dictionary of the form
# I'm currently using for AgeMatchedDict.p, and then 
# writes a tab-delimited file with it. 


def orangify(inDict):
    """
    Takes inDict dictionary and
    writes the contents to a "*.tab"
    file for machine learning in Orange
    """
    import sys

    #--------------------------------
    # Write the headers to the outfile
    #--------------------------------

    # Generate the header names
    regions = ['lf', 'rf', 'lp', 'rp', 'o']
    conditions = ['eo', 'ec']
    coeffs = ['c1', 'c2', 'c3', 'c4', 'c5']
    stats = ['max', 'mean']

    # Subject ID is the first column
    sys.stdout.write("%s\t" % "sID")

    # Diagnosis second
    sys.stdout.write("%s\t" % "Dx")

    # Age third
    sys.stdout.write("%s\t" % "Age")

    nCols = 3

    # Write coefficient headers
    for condition in conditions:
        for region in regions:
            for coeff in coeffs:
                sys.stdout.write("%s\t" % (region + "_" + condition + "_" + coeff))
                nCols += 1
                # Write mean/max headers
    for condition in conditions:
        for region in regions:
            for stat in stats:
                sys.stdout.write("%s\t" % (region + "_" + condition + "_" + stat))
                nCols += 1

    sys.stdout.write("\n")

    #---------------------------------
    # Write the variable types (continuous/discrete/etc)
    #---------------------------------

    # Call sID continuous
    sys.stdout.write("%s\t" % "c")

    # Diagnosis is discrete, 'ADHD' or 'CONTROL'
    sys.stdout.write("%s\t" % "d")

    # Everything else is continuous
    for i in range(nCols - 2):
        sys.stdout.write("%s\t" % "c")

    sys.stdout.write("\n")

    #--------------------------------
    # Write variable types (class/meta/ignore)
    #--------------------------------

    # sID is a meta-attribute
    sys.stdout.write("%s\t" % "meta")

    # Diagnosis is the class attribute
    sys.stdout.write("%s\t" % "class")

    # Nothing else is special
    sys.stdout.write("\n")

    #-------------------------------
    # Write subject data, one subject per row
    #-------------------------------

    regions = ['left_frontal', 'right_frontal', 'left_parietal', 'right_parietal', 'occipital']

    for sub in sorted(inDict.keys()):
        # print the subject number
        sys.stdout.write("%s\t" % sub)

        # print the diagnosis
        sys.stdout.write("%s\t" % inDict[sub]['Dx'])

        # Write age
        sys.stdout.write("%f\t" % float(inDict[sub]['age']))

        # Now loop over features in order
        for condition in conditions:
            if condition in inDict[sub]:
                for region in regions:
                    for coeff in inDict[sub][condition][region]['coeffs']:
                        sys.stdout.write("%f\t" % coeff)
            else:
                # If they don't have eo/ec data, leave blank spaces
                sys.stdout.write("\t" * len(regions) * len(coeffs))

        # Write mean/max stats
        for condition in conditions:
            if condition in inDict[sub]:
                for region in regions:
                    for stat in stats:
                        sys.stdout.write("%f\t" % inDict[sub][condition][region][stat])
            else:
                # If they don't have eo/ec data, leave blank spaces
                sys.stdout.write("\t" * len(regions) * len(stats))

        # New line
        sys.stdout.write("\n")


if __name__ == "__main__":
    import cPickle as pickle
    import sys

    with open(sys.argv[1], "r") as inFile:
        subDict = pickle.load(inFile)
        orangify(subDict)


