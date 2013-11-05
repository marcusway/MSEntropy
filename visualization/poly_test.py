import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import cPickle as pickle
import scipy.stats


pdf = PdfPages('polyFind' + '.pdf')

a = pickle.load(open("AgeMatchedDict.p","r"))
regions = ['left_frontal','right_frontal','left_parietal','right_parietal','occipital']
conditions = ['eo','ec']

def plot_poly(x,polyList):
	degree = len(polyList)

	return [sum(polyList[degree-1-i]* j**i for i in range(degree)) for j in x]

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
        a[subject][condition][region]['mse'] for subject in a if condition in a[subject]]
        #and a[subject]['Dx'] == 'ADHD' and int(subject) > 1037]

        # print "ADHD: ", [subject for subject in a if condition in a[subject]
        #     and a[subject]['Dx'] == 'ADHD']# and int(subject) > 1037]

        # print "ADHD:", [subject for subject in a if condition in a[subject]
        #     and a[subject]['Dx'] == 'ADHD']

        average_ADHD = np.mean(ADHD,0)

        x = range(20)
        for degree in range(1,4):
        	polyList = np.polyfit(x,average_ADHD,degree)
        	y = plot_poly(x, polyList)
        	plt.plot(x,y)


        plt.plot(range(20),average_ADHD, "-o")
        #plt.xlabel("Scale")
        plt.ylabel("mSampEn")
        plt.legend(["1","2","3","Real"], loc=4)
        plt.title(region)


    pdf.savefig(fig)
    plt.close()
pdf.close()
