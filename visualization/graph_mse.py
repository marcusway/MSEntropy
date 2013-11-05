__author__ = 'marcusway'



"""
A script to plot the multi-scale entropy for given
subjects/channels given an input file containing
all the mse information (output from computeMSE_orangeFormat.py).
To run the script, type at the command line: 
python graph_mse.py <filename here>
"""


def graph_mse(filename):
    import matplotlib.pyplot as plt
    plt.ioff() # make sure interactive mode is off so plots are saved automatically
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib
    import numpy as np
    import sys
    from data_manipulation import *
    matplotlib.rcParams.update({'font.size': 4})


    ns = 40
    nChannels = 129
    FOCUS_electrodes = dict(left_frontal=[28, 24, 19], right_frontal=[4, 124, 117],
                            left_parietal=[52, 53, 60], right_parietal=[85, 86, 92],
                            occipital=[70, 75, 83])

    if 'eo' in filename:
        condition = 'eo'
    elif 'ec' in filename:
        condition = 'ec'
    else:
        print 'Eyes open/closed not specified in filename'
        sys.exit()


    # Read in the file using my made-up function
    header_row, header_col, mse_data = get(filename)
    print 'HEADER ROW: ', header_row[0:10], '...'
    print 'HEADER COL: ', header_col[0:10], '...'
    print 'length of data:', len(mse_data), 'shape of data', mse_data.shape, 'number of entries per row: ', len(
        mse_data[0])

    # We should have a situation here where there are (entropy scales)*(number of channels) entries in each row
    nExpected = nChannels * ns
    nRead = len(mse_data[0])

    # Report an error if above is not the case
    if nRead != nExpected:
        print 'Expected ', nExpected, 'datapoints per subject.  read ', nRead
        sys.exit()

    path_to_file = '/Users/margaretsheridan/Desktop'
    pdf = PdfPages(path_to_file + 'SAS_MSE_eo' + condition + '.pdf')
    subject_index = 0

    for subject in mse_data:
        subID = header_col[subject_index]
        print 'starting on subject', subID

        subject_index += 1

        fig = plt.figure(figsize=(4, 6))
        fig.text(.5, .95, subID, horizontalalignment='center')
        subplot_index = 1

        for region in FOCUS_electrodes:

            plt.subplot(3, 2, subplot_index)
            subplot_index += 1

            for electrode in FOCUS_electrodes[region]:
                # Since every twenty values in subject are from the same electrode, we are looking for the
                # twenty values that correspond to the electrode we're looking at, which should start at
                # 20*(channel # - 1) and continue on to 20*(channel # -1) + 20

                lower_index = ns * (electrode - 1) # subtract 1 from electrode number since this is zero-indexed
                upper_index = ns * (electrode - 1) + ns
                mse = np.array(subject[lower_index:upper_index])
                #inflection_x, inflection_y = distill_mse.get_inflection_point(mse)
                # minimum, maximum, slope, mean = distill_mse.get_max_min_slope(mse)

                if len(mse) == 0:
                    print 'DONE'
                    break

                plt.plot(range(1, ns + 1), mse)
                #plt.plot(inflection_x+1,inflection_y,'x')
                plt.title(region)

        pdf.savefig(fig)
        plt.close()

    pdf.close()

if __name__ == "__main__":
    import sys
    graph_mse(sys.argv[1])









