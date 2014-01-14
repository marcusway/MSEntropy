from collections import OrderedDict
import matplotlib.pyplot as plt
import numpy as np
import cPickle as pickle
from matplotlib.backends.backend_pdf import PdfPages
import scipy.stats

pdf = PdfPages('remitMSE_nofill' + '.pdf')

a = pickle.load(open("../../Data/datasets/pickledData/Focus_dict.p","r"))
regions = OrderedDict([('left_frontal', 'Left Frontal'), ('right_frontal', 'Right Frontal'),
            ('left_parietal','Left Parietal'), ('right_parietal', 'Right Parietal'), ('occipital', 'Occipital')])
conditions = OrderedDict([('eo', 'Eyes Open'),('ec', 'Eyes Closed')])

for condition in conditions:

    fig = plt.figure(figsize=(8, 11))
    fig.text(.5, .95, conditions[condition], horizontalalignment='center')
    subplot_index = 1

    for region in regions:

        plt.subplot(3, 2, subplot_index)
        subplot_index += 1

        ADHD = [
        a[subject][condition][region]['mse'] for subject in a if condition in a[subject]
        and a[subject]['non_remit'] is True]# and int(subject) > 1037]

        # print "ADHD: ", [subject for subject in a if condition in a[subject]
        #     and a[subject]['Dx'] == 'ADHD']# and int(subject) > 1037]

        # print "ADHD:", [subject for subject in a if condition in a[subject]
        #     and a[subject]['Dx'] == 'ADHD']

        CONTROL = [
            a[subject][condition][region]['mse'] for subject in a if condition in a[subject] and a[subject]['non_remit'] is False]# and int(subject)>1037]
        # print "CONTROLS: ", [subject for subject in a if condition in a[subject]
        #     and a[subject]['Dx'] == 'CONTROL' and int(subject) > 1037]
        
        # print "Controls:", [subject for subject in a if condition in a[subject]
        #     and a[subject]['Dx'] == 'CONTROL']

        average_ADHD = np.mean(ADHD,0)
        average_CONTROL = np.mean(CONTROL,0)

        print "average_ADHD = ", average_ADHD
        # print "AVERAGE ADHD:", average_ADHD
        # print "AVERAGE CONTROL:", average_CONTROL

        ADHD_stderr = scipy.stats.sem(ADHD,0)#/np.sqrt(np.shape(average_ADHD)[0])
        CONTROL_stderr = scipy.stats.sem(CONTROL,0)#/np.sqrt(np.shape(average_CONTROL[0]))
        print "ADHD_stderr = ", ADHD_stderr

        print scipy.stats.ttest_ind(ADHD,CONTROL, axis=0)[1]
        x = range(1,21)
        print "len(avg_adhd): %d, len(adhd_stderr) = %d, len(control_avg) = %d, len(control_stderr) = %d" %(len(average_ADHD), len(ADHD_stderr), len(average_CONTROL), len(CONTROL_stderr))
        print np.array(average_ADHD - ADHD_stderr)
        plt.plot(x,average_ADHD, color="r", linewidth=2, aa=True)
        #plt.fill_between(x, average_ADHD-ADHD_stderr, average_ADHD + ADHD_stderr, facecolor='r', alpha=0.2)

        plt.errorbar(x,average_CONTROL, color="b", linewidth=2, aa=True)
        #plt.fill_between(x, average_CONTROL - CONTROL_stderr, average_CONTROL + CONTROL_stderr, facecolor='b', alpha=0.2)
        plt.legend(["ADHD (unlikely to remit)","Controls & Likely Remitters"], loc=4, fontsize=10)
        #plt.fill_between(x, average_CONTROL + CONTROL_stderr, average_ADHD - ADHD_stderr, where=average_CONTROL + CONTROL_stderr > average_ADHD - ADHD_stderr, facecolor='', alpha=0.5)

       # plt.xlabel("Scale")
    #plt.ylabel("mSampEn")
        plt.title(regions[region])

    pdf.savefig(fig)
    plt.close()
pdf.close()
        


