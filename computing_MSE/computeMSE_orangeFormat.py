###############################################################################
#   computeMSE_orangeFormat.py                                                #
#                                                                             #
#   A script that reads multiple input files, each of which should contain    #
#   time series data, where each row represents the time series data for a    #
#   single channel.  Presence or absence of header rows/columns in the        #
#   input files should be noted at the command line. Note that the .txt files #
#   produced as output by eeglab that we have been using (in files like       #
#   ADHD_1054eor.txt) DO have header rows and columns.                        #
#                                                                             #
#   written by Marcus Way, using Bill Bosl's implementation of the            #
#   multiscale entropy calculation algorithm where the length of              #
#   the embedding vector, m = 2, and a tolerance factor, r = 0.15.            #
#                                                                             #
###############################################################################


#-----------------------
# IMPORTS
#-----------------------
import numpy as np
import mse
import argparse
import os
import re
import data_manipulation as dm
import scipy.signal as sig

#---------------------
# Initializations
#---------------------
SAMPLING_RATE = 250.0
nyquist = SAMPLING_RATE/2

# Allow user to set some parameters from the command line
parser = argparse.ArgumentParser(
    description='''
                Reads multiple files
                containing raw EEG data and
                computes MSE values for the
                given number of scales.
                '''
)

# The first positional argument will be a template
# for the multi-channel time series data files to
# for which MSE is being calculated
parser.add_argument("inFileList", nargs="*")

# The second positional argument will designate the
# output file template.  To output files will be saved,
# one for eyes open and one for eyes closed.
parser.add_argument("outFileTemplate")

# Optional arguments include adjustments to the number of scales
# and number of channels (rows in input files)
parser.add_argument("-ns", "--nScales", default=20, type=int,
                    help="the number of scales at which "
                         "entropy will be calculated. default"
                         "=20\n"
)

parser.add_argument("-nc", "--nChannels", default=129, type=int,
                    help="Number of electrodes per subject. "
                         "default = 129\n"
)


# Specify whether or not input files have headers
parser.add_argument("-hr", "--headerRow", action="store_false",
                    help="use flag if input files DO NOT contain "
                         "a header row\n"
)
parser.add_argument("-hc", "--headerCol", action="store_false",
                    help="use if input files DO NOT contain "
                         "a header column\n"
)


# User may also use the --downSample option to specify
# subjects for whom s/he would like to use a version of
# the input time series that is down-sampled by a
# factor of two (include subjects sampled at 500 Hz)
parser.add_argument("-d", "--downSample", nargs="+", default=[],
                    help="use flag to specify subjects "
                         "whose time series data must be down-sampled "
                         "prior to MSE calculation.  Subject numbers "
                         "should follow this argument, separated "
                         "by spaces. For example,\n"
                         "python computeMSE_orangeFormat.py inFile*.txt, outFile.txt -d 1004 1005 "
                         "would run MSE calculation for all files that fit the in file template, but "
                         "would specifically downsample the input data for subjects 1004 and 1005"
)

# Specify the amount of output printed to the terminal
parser.add_argument("-v", "--verbose", action="store_true")

# Specify if you want to append to existing files
parser.add_argument("-a", "--appendToFile", action="store_true")

# Toggle 60Hz notch filter on/off
parser.add_argument("-f", "--filter", action="store_true", help="Notch filter time series at 58-62 Hz")

# Evaluate command line input
args = parser.parse_args()

# Initialize emtpy Numpy array for entropy
entropy = np.zeros(args.nScales, 'double')

# Open two output files, one for EO, one for EC

# Append suffix for eyes open or eyes closed
# for different output files
outName, outExtension = os.path.splitext(args.outFileTemplate)
eoOutName = outName + "_eo" + outExtension
ecOutName = outName + "_ec" + outExtension

# Open the files for writing or appending
# Right now, I'm just going to always open
# in append mode to avoid overwriting files.
# If someone specifies the outfile to be one
# that already exists but fails to specify that
# they're using append mode at the command line
# they'll just get an extra header row in the
# file existing file.  So it's impossible to
# overwrite a pre-existing file as is.

eo_outfile = open(eoOutName, "a")
ec_outfile = open(ecOutName, "a")

#------------------------------------
# Write headers to the output files.
#------------------------------------

# We only want to write headers if we're not
# in append mode, i.e., we're not adding to
# pre-existing files.  As it is set up right now,
# _eo and corresponding _ec files are assumed to
# either both be present or both be absent.

# Write the header row for each file
if not args.appendToFile:
    for outFileName in [eoOutName, ecOutName]:
        outFile = open(outFileName, "a")
        outFile.write("SubID\t")
        for c in range(1, args.nChannels + 1):
            for s in range(args.nScales):
                outFile.write("c%d_s%d\t" % (c, s))
        outFile.write("\n")
        outFile.close()

#-------------------------------------------------------------------
# Get the file name, read the data, compute mse and write to file.
#-------------------------------------------------------------------
nFiles = len(args.inFileList)
print "Total files to process: %d\n" % nFiles
files_processed = 0
for fname in args.inFileList:

    # VERBOSE MODE STATUS UPDATE
    if args.verbose:
        print "Processing file %s . . ." % fname

    #----------------------------------------------------------
    # HARD-CODED FOCUS-SPECIFIC FILE NAME STUFF
    #-----------------------------------------------------------

    # Just look for a number in the file name, and assume it's the subject number for now
    IDList = re.findall(r'\d+', os.path.basename(fname))

    # There should be exactly one string of numbers in the file name.
    # If this is not the case, inform the user and skip this file.
    if len(IDList) != 1:
        print "Can't determine subject ID from file name: %s. Skipping this file." % fname
        continue
    else:
        ID = IDList[0]

    # Use the file name to determine whether to write to the eyes open or eyes closed file
    if 'eo' in fname:
        fout = open(eoOutName, "a")
    elif 'ec' in fname:
        fout = open(ecOutName, "a")
    else:  # If eo or ec not specified in file name, report an error and skip the file
        print "Problem with file: %s.  It doesn\'t have an ''eo'' or ''ec'' in its name. Skipping this file." % fname
        continue

    #----------------------------------------
    # INPUT CHECKING
    #----------------------------------------

    # Read data from file into a 2-dimensional numpy array
    _, _, data = dm.get(fname, headerRow=args.headerRow, headerCol=args.headerCol)

    # Calculate number of channels and time points in a series
    nc_read, nt = data.shape
    if args.verbose:
        print "Number of electrodes: %d" % nc_read
        print "Number of time points: %d" % nt

    # If the number of channels in the file is different from what's expected,
    # print a message and exit.
    if nc_read != args.nChannels:
        print "Number of channels = %d; expected number = %d" % (nc_read, args.nChannels)
        exit()

    #--------------------------------------------
    # MSE COMPUTATION
    #--------------------------------------------
    entropyArray = []
    for channel in range(args.nChannels):

        timeSeries = data[channel]

        # If this subject is one of the subjects indicated
        # to be down-sampled at the command line
        if ID in args.downSample:
            if args.verbose:
                print "Down sampling input time series for subject: %s, channel: %d" % (ID, channel + 1)

            # Take every other point in the original time series
            timeSeries = [timeSeries[i] for i in range(0, nt, 2)]

            if args.verbose:
                print "Number of time points in new time series: %d" % len(timeSeries)

        

        # Apply 60 Hz notch filter if spcecified in command line
        if args.filter is True:
            b, a = sig.butter(4, (58/(nyquist), 62/nyquist), btype='bandstop')
            timeSeries = sig.filtfilt(b, a, timeSeries)
            if args.verbose:
                print "Filtering out 60Hz noise"

        if args.verbose:  # if user specified verbose mode, update channel by channel
            print "Calculating MSE for subject %s, channel %d" % (ID, channel + 1)
            
        # Make the actual entropy calculation
        MSEntropy = mse.mse(timeSeries, entropy)

        # Tell the user
        if args.verbose:
            print "MSE calculation for subject %s channel %d complete:" % (ID, channel + 1)
            print MSEntropy

        # Add the new entropy values to the list for the current subject.
        entropyArray.extend(MSEntropy)

    #--------------------------------------
    # FILE WRITING
    #--------------------------------------
    if args.verbose:
        print "\nSuccessfully calculated MSE for all electrodes for subject %s. Writing data to file." % ID

    # Write the subject's ID to the output file
    fout.write("%s\t" % ID)

    # Write all entropy calculations
    for dataPoint in entropyArray:
        fout.write("%lf\t" % dataPoint)

    # Continue to the next file
    fout.write("\n")
    fout.close()
    files_processed += 1
    print 'Completed Files: %d/%d' % (files_processed, nFiles)

if args.verbose:
    print "\nExecution complete.  Successfully processed %d of %d input files" % (files_processed, nFiles)

