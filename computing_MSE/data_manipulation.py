__author__ = "Marcus Way"


def get(filename, headerRow=True, headerCol=True):
    """
    By default, reads in a data file, returns a list of the top row entries as
    'header_row', returns a list of the first column entries as
    'header_col', and the rest of the entries as a numpy array. Can indicate whether
    the input file, filename, uses headers via the keyword arguments headerRow and
    headerCol, both of which are True by default.  If False, an empty list is
    returned for the corresponding header in the return values.

    :param headerRow:
        True if the first row of the file specified by
        filename is a header row
    :param headerCol:
        True if the first column of the file specified
        by filename is a header column
    :param filename:
        A string that specifies the path to a
        data file where the first row is a
        header row, and the first column is
        a header column.

    :return header_row, header_col, np.array(data):
        header_row is a list object containing
        the the items in the header row, in
        order of appearance in the input file.
        header_col is also a list object,
        containing the items in the header
        row in the order of appearance in the
        input file, from left to right.
        np.array(data) is a numpy array object
        in which the rows correspond to
        electrodes and the columns correspond to
        scales.

    """

    import numpy as np

    # Initialize headers.  As is, function will return
    # empty lists for header_row and header_col if
    # the keyword arguments are False.
    header_col = []
    header_row = []

    data = []

    with open(filename, 'rU') as in_file:
        if headerRow:
            header_row = in_file.readline().split()  # Set header_row to be the first line
        line_counter = 1  # Keep track of the line number for error reporting
        for line in in_file:
            line_counter += 1
            line_list = line.split()
            if headerCol:
                header_col.append(line_list.pop(0))  # Add the first (column) entry of each row to the header_col list
            try:
                # Convert the rest of the entries to floating point values, add to the data
                data.append([float(i) for i in line_list])
            except ValueError:
                print 'Can\'t convert line', line_counter, 'which looks like this:\n', line[0:10]

    return header_row, header_col, np.array(data)  # convert 'data' to a multidimensional array


def dictify(MSE_filename, nScales=20):
    """
    This function takes the spreadsheet, MSE_filename
    of the format output by the script computeMSE_orangeFormat.py
    (a tab-separated spreadsheet with a header column containing
    subject numbers and a header row with entries like c13_s3,
    which would correspond to channel 13, scale 3.

    :param nScales: number of entropy scales for each channel
                    in the input spreadsheet
    :rtype : dict object
    :param MSE_filename:

    A string specifying the path
    to the file containing MSE
    data.  The file should have a
    header row specifying channel/scale
    data and a header column containing
    subject IDs.  The subject IDs will
    be used as dictionary keys for the output

    :return: outDict

    A dictionary whose keys correspond to the
    the values of the first column. These should
    be subject ID numbers if the input parameter
    specifies the path to a file of the correct format.
    Each item in the dictionary will be an array
    of size nChannels x nScales.

    Example:
            # Generate a new dictionary
            eoDict = dictify('MSE_eo.txt')

            # Get the entropy value for subject 1084
            # at channel 124, scale 0.  Note that the
            # channel numbers are zero-indexed here, but
            # they are 1-indexed in Net Station and MATLAB
            # so in order to access a given channel in this
            # dictionary, subtract one from its Net Station
            # channel number.
            eoDict[subNum][123][0]
    """

    # Load the file
    header_row, header_col, data = get(MSE_filename)

    # Make a dictionary with subject numbers as keys
    outDict = {}
    for subject, entropy in zip(header_col, data):
        # Add a key for each subject, whose corresponding entry
        # will be a nChannels x nScales numpy array
        outDict[subject] = [entropy[j:j + nScales] for j in range(0, len(entropy), nScales)]

    return outDict


def save_dict(MSE_filename, out_file_name):
    """

    :param MSE_filename:

    A string specifying the path
    to the file containing MSE
    data.  The file should have a
    header row specifying channel/scale
    data and a header column containing
    subject IDs.  The subject IDs will
    be used as dictionary keys for the output

    :param out_file_name:

    A string specifying the path to (and name of)
    the output file, which will contain a pickled
    dictionary, where the subject IDs are used
    as keys to entries consisting of 2-D arrays
    of MSE data, where each row is a channel
    and each column is a scale.
    """
    import cPickle as pickle

    sub_dict = dictify(MSE_filename)

    with open(out_file_name, 'wb') as fp:
        pickle.dump(sub_dict, fp)


def make_FOCUS_dict(eyes_closed_file_name, eyes_open_file_name, subject_info_file_name=None, FOCUS_dict={}):
    """
    Loads dictionaries containing the mse
    data and a .csv file with diagnosis 
    information. It's formulated in this way
    for purely ad hoc reasons. Make sure that
    the .csv file has a column with the header
    'finalDx'. This function is highly specific
    to the exigencies of the current study.

    :param eyes_closed_file_name:
        path to a pickled Python
        dictionary file containing
        eyes open data
    :param eyes_open_file_name:
        path to a pickled Python
        dictionary file containing
        eyes open data
    :param subject_info_file_name:
        path to a .csv spreadsheet
        containing subject diagnosis
        information.  The program assumes
        that there will be headers 'sID'
        for the subject ID number column
        and 'finalDx' for the diagnosis
        column.
    :rtype : dict object
    :return FOCUS_dict:
        A dictionary with subject numbers
        for keys.  Each subject key has
        average MSE data across electrodes at all scales
        for each region for both eo/ec (if the data exists).
        Each subject also has diagnosis information.

    """
    import numpy as np
    import cPickle as pickle
    import csv
    import distill_mse

    # Define FOCUS electrodes, grouped by region
    FOCUS_electrodes = {'left_frontal': [28, 24, 19], 'right_frontal': [4, 124, 117],
                        'left_parietal': [52, 53, 60], 'right_parietal': [85, 86, 92],
                        'occipital': [70, 75, 83]}

    conditions = ["eo", "ec"]

    # Load all of the raw data:
    with open(eyes_closed_file_name, 'rb') as ecFile:
        with open(eyes_open_file_name, 'rb') as eoFile:
            ec_dict, eo_dict = pickle.load(ecFile), pickle.load(eoFile)

            # Only add an 'eo' or 'ec' key if data for the respective condition exists
            for eo_sub in eo_dict:
                FOCUS_dict[eo_sub] = {}
                FOCUS_dict[eo_sub]['eo'] = {}
            for ec_sub in ec_dict:
                if ec_sub not in FOCUS_dict:
                    FOCUS_dict[ec_sub] = {}
                FOCUS_dict[ec_sub]['ec'] = {}

            # Do data processing steps for each subject
            for sub in FOCUS_dict:
                for group, condition in zip([eo_dict, ec_dict], conditions):
                    if sub in group:
                        for region in FOCUS_electrodes:
                            # Make a new dictionary for the region
                            FOCUS_dict[sub][condition][region] = {}
                            # Add entry for the average mse (across electrodes) data for the region
                            FOCUS_dict[sub][condition][region]['mse'] = np.mean(
                                np.array([ec_dict[sub][channel - 1] for channel in FOCUS_electrodes[region]]), 0)
                            # Add entries for max, mean of new region mse data
                            FOCUS_dict[sub][condition][region]['mean'] = np.mean(
                                FOCUS_dict[sub][condition][region]['mse'])
                            FOCUS_dict[sub][condition][region]['max'] = np.max(
                                FOCUS_dict[sub][condition][region]['mse'])
                            FOCUS_dict[sub][condition][region]['coeffs'] = \
                                distill_mse.fit(FOCUS_dict[sub][condition][region]['mse'], degree=4)

            # Add Dx information to each subject
            if subject_info_file_name:
                with open(subject_info_file_name, 'rU') as f:
                    reader = csv.DictReader(f)

                    for subject in reader:
                        if subject['sID'] in FOCUS_dict:
                            if float(subject['finalDx']) == 1:
                                FOCUS_dict[subject['sID']]['Dx'] = 'ADHD'
                            if float(subject['finalDx']) == 0:
                                FOCUS_dict[subject['sID']]['Dx'] = 'CONTROL'

                            # Add the subject's age to the dictionary
                            FOCUS_dict[subject['sID']]['age'] = subject['age']

            return FOCUS_dict