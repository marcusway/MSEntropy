import Orange
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

data = Orange.data.Table("entropy_orange.tab")
maxFolds = 74
maxNeighbors = 74

accuracy_array = np.zeros((maxFolds, maxNeighbors))

for nFolds in range(1,maxFolds):
	for nNeighbors in range(1,maxNeighbors):
# tree = Orange.classification.tree.TreeLearner()
# tree.name = "tree"
# nbc = Orange.classification.bayes.NaiveLearner()
# nbc.name = "nbc"
# svm = Orange.classification.svm.SVMLearner()
# svm.name = "svm"
		knn = Orange.classification.knn.kNNLearner(k=nNeighbors, rank_weight = False)
		knn.name = 'knn'
		learners = [knn]
		#print " "*9 + " ".join("%-4s" % learner.name for learner in learners)
		res = Orange.evaluation.testing.cross_validation(learners, data, folds=nFolds)
		#print "Accuracy %s" % " ".join("%.2f" % s for s in Orange.evaluation.scoring.CA(res))
		#print "AUC      %s" % " ".join("%.2f" % s for s in Orange.evaluation.scoring.AUC(res))
		accuracy_array[nFolds][nNeighbors] = Orange.evaluation.scoring.CA(res)[0]
		print "Folds = ", nFolds, "neighbors =", nNeighbors, "accuracy = ", accuracy_array[nFolds][nNeighbors]

best_accuracy = np.max(accuracy_array)
best_accuracy_coords = np.unravel_index(np.argmax(accuracy_array),np.shape(accuracy_array))
print "\n\n\n The winner is:", np.max(accuracy_array), "from folds =", best_accuracy_coords[0], "k = ", best_accuracy_coords[1]

# Plot the results 
X = np.arange(maxFolds)
Y = np.arange(maxNeighbors)
X, Y = np.meshgrid(X, Y)
Z = accuracy_array
fig = plt.figure()
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm)
ax.set_zlim(0,1)
ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
fig.colorbar(surf,shrink=0.5,aspect = 5)

plt.show()

