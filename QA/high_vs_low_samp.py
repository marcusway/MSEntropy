import matplotlib.pyplot as plt
import numpy as np
import cPickle as pickle
from matplotlib.backends.backend_pdf import PdfPages
import scipy.stats

pdf = PdfPages('SamplingRate' + '.pdf')

a = pickle.load(open("Age_matched_w_inner_and_outer.p","r"))
regions = ['left_frontal','right_frontal','left_parietal','right_parietal','occipital']
conditions = ['eo','ec']

for condition in conditions:

    fig = plt.figure(figsize=(8, 11))
    fig.text(.5, .95, condition, horizontalalignment='center')
    subplot_index = 1

    for region in regions:

        plt.subplot(3, 2, subplot_index)
        subplot_index += 1

        LOW = [
        a[subject][condition][region]['mse'] for subject in a if condition in a[subject]
        and a[subject]['Dx'] == 'CONTROL' and int(subject) > 1037]

        print "250:",[sub for sub in a if int(sub)>1037 and a[sub]['Dx']=='CONTROL']

        # print "ADHD:", [subject for subject in a if condition in a[subject]
        #     and a[subject]['Dx'] == 'ADHD']

        HIGH = [
            a[subject][condition][region]['mse'] for subject in a if condition in a[subject] and a[subject]['Dx'] == 'CONTROL' and int(subject) < 1038]
        print "500:",[sub for sub in a if int(sub) <= 1037 and a[sub]['Dx'] == 'CONTROL']

        # All_subs
        # print "Controls:", [subject for subject in a if condition in a[subject]
        #     and a[subject]['Dx'] == 'CONTROL']
        average_LOW= np.mean(LOW,0)
        average_HIGH = np.mean(HIGH,0)

        # print "AVERAGE ADHD:", average_ADHD
        # print "AVERAGE CONTROL:", average_CONTROL

        LOW_stderr = scipy.stats.sem(average_LOW,0)#/np.sqrt(np.shape(average_ADHD)[0])
        HIGH_stderr = scipy.stats.sem(average_HIGH,0)#/np.sqrt(np.shape(average_CONTROL[0]))

        #print scipy.stats.ttest_ind(LOW,HIGH, axis=0)[1]

        plt.errorbar(range(1,21),average_LOW, yerr=LOW_stderr, xerr=None, color="b")

        plt.errorbar(range(1,21),average_HIGH, yerr=HIGH_stderr, xerr=None, color="r")

        # plt.plot(range(1,21),average_ADHD,"r")
        # plt.plot(range(1,21),average_CONTROL,"b")
        # #plt.xlabel("Scale")
        # plt.ylabel("mSampEn")
        plt.title(region)
        plt.legend(['250Hz', '500Hz'], loc=4)

    pdf.savefig(fig)
    plt.close()
pdf.close()
        


