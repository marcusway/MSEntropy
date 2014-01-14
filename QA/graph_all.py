import matplotlib.pyplot as plt
import numpy as np
import cPickle as pickle
from matplotlib.backends.backend_pdf import PdfPages
import scipy.stats

#------------------------
# GET AVERAGE FOR INNER AND OUTER 
#------------------------
inner = [7, 6, 106, 55, 12,5, 29, 30, 31, 112, 105, 80, 54, 79, 62]
outer = [128, 48, 49, 56, 63, 68, 73, 81, 88, 94, 99, 107, 113, 119, 125]

inner_electrodes = [i-1 for i in inner]
outer_electrodes = [i-1 for i in outer]
#random.seed(time.time())
#inner_electrodes = [random.choice(all_channels) for i in range(15)]
#outer_electrodes = [random.choice(all_channels) for i in range(15)]


eo = pickle.load(open("mse_eo_dict.p","r"))
ec = pickle.load(open("mse_ec_dict.p","r"))
matched = pickle.load(open("matched.p","r"))

eo_outer_entropy = [np.mean([eo[sub][electrode] for electrode in range(129) if electrode in outer_electrodes],0) for sub in eo if sub in matched]
eo_inner_entropy = [np.mean([eo[sub][electrode] for electrode in range(129) if electrode in inner_electrodes],0) for sub in eo if sub in matched]

ec_outer_entropy = [np.mean([ec[sub][electrode] for electrode in range(129) if electrode in outer_electrodes],0) for sub in ec if sub in matched]
ec_inner_entropy = [np.mean([ec[sub][electrode] for electrode in range(129) if electrode in inner_electrodes],0) for sub in ec if sub in matched]

avg_eo_outer = np.mean(eo_outer_entropy,0)
avg_eo_inner = np.mean(eo_inner_entropy,0)

avg_ec_outer = np.mean(ec_outer_entropy,0)
avg_ec_inner = np.mean(ec_inner_entropy,0)

extrema = {'eo': {'inner': avg_eo_inner, 'outer':avg_eo_outer}, 'ec': {'inner': avg_ec_inner, 'outer': avg_ec_outer}}
#----------------------------------------------------------

pdf = PdfPages('average_mse_plots_w_inner_and_outer' + '.pdf')

a = pickle.load(open("Age_matched_focus_dict.p","r"))
regions = ['left_frontal','right_frontal','left_parietal','right_parietal','occipital']
conditions = ['eo','ec']

for condition in conditions:

    fig = plt.figure(figsize=(8, 11))
    fig.text(.5, .95, condition, horizontalalignment='center')
    subplot_index = 1

    for region in regions:

        plt.subplot(3, 2, subplot_index)
        subplot_index += 1

        ADHD = [
        a[subject][condition][region]['mse'] for subject in a if condition in a[subject]
        and a[subject]['Dx'] == 'ADHD']

        # print "ADHD:", [subject for subject in a if condition in a[subject]
        #     and a[subject]['Dx'] == 'ADHD']

        CONTROL = [
            a[subject][condition][region]['mse'] for subject in a if condition in a[subject] and a[subject]['Dx'] == 'CONTROL']


        # print "Controls:", [subject for subject in a if condition in a[subject]
        #     and a[subject]['Dx'] == 'CONTROL']
        average_ADHD = np.mean(ADHD,0)
        average_CONTROL = np.mean(CONTROL,0)

        # print "AVERAGE ADHD:", average_ADHD
        # print "AVERAGE CONTROL:", average_CONTROL

        ADHD_stderr = scipy.stats.sem(average_ADHD,0)
        CONTROL_stderr = scipy.stats.sem(average_CONTROL,0)

        # print scipy.stats.ttest_ind(ADHD,CONTROL, axis=0)[1]

        # plt.errorbar(range(1,21),average_ADHD, yerr=ADHD_stderr, xerr=None, color="b")

        # plt.errorbar(range(1,21),average_CONTROL, yerr=CONTROL_stderr, xerr=None, color="r")

        plt.plot(range(20),average_ADHD)
        plt.plot(range(20),average_CONTROL)
        plt.plot(range(20), extrema[condition]['inner'])
        plt.plot(range(20), extrema[condition]['outer'])
        #plt.xlabel("Scale")
        plt.ylabel("mSampEn")
        plt.legend(('ADHD','Control','Inner Electrodes','Outer Electrodes'), loc=4, prop={'size':6})
        plt.title(region)

    pdf.savefig(fig)
    plt.close()
pdf.close()
        


