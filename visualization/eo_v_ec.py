import matplotlib.pyplot as plt
import numpy as np
import cPickle as pickle
from matplotlib.backends.backend_pdf import PdfPages
import scipy.stats

pdf = PdfPages('eo_vs_ec_before1037' + '.pdf')

a = pickle.load(open("AgeMatchedDict.p","r"))
regions = ['left_frontal','right_frontal','left_parietal','right_parietal','occipital']
conditions = ['eo','ec']

fig = plt.figure(figsize=(8, 11))
fig.text(.5, .95, 'EO vs EC', horizontalalignment='center')
subplot_index = 1

for region in regions:

    plt.subplot(3, 2, subplot_index)
    subplot_index += 1

    ADHD = [
    a[subject]['eo'][region]['mse'] for subject in a if 'eo' in a[subject]
    and int(subject) < 1037]


    # print "ADHD:", [subject for subject in a if condition in a[subject]
    #     and a[subject]['Dx'] == 'ADHD']

    CONTROL = [
        a[subject]['ec'][region]['mse'] for subject in a if 'ec' in a[subject] and int(subject)<1037]
    
    # print "Controls:", [subject for subject in a if condition in a[subject]
    #     and a[subject]['Dx'] == 'CONTROL']
    average_ADHD = np.mean(ADHD,0)
    average_CONTROL = np.mean(CONTROL,0)

    # print "AVERAGE ADHD:", average_ADHD
    # print "AVERAGE CONTROL:", average_CONTROL

    ADHD_stderr = scipy.stats.sem(average_ADHD,0)#/np.sqrt(np.shape(average_ADHD)[0])
    CONTROL_stderr = scipy.stats.sem(average_CONTROL,0)#/np.sqrt(np.shape(average_CONTROL[0]))

    #print scipy.stats.ttest_ind(ADHD,CONTROL, axis=0)[1]

    plt.errorbar(range(1,21),average_ADHD, yerr=ADHD_stderr, xerr=None, color="b")

    plt.errorbar(range(1,21),average_CONTROL, yerr=CONTROL_stderr, xerr=None, color="r")
    plt.legend(["EO","EC"], loc=4)


    # plt.plot(range(1,21),average_ADHD,"r")
    # plt.plot(range(1,21),average_CONTROL,"b")
    # #plt.xlabel("Scale")
    # plt.ylabel("mSampEn")
    plt.title(region)
plt.close()
pdf.savefig(fig)
pdf.close()
        


