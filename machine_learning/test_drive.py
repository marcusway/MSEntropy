import Orange
import sys

# to_exclude = [['age'],['gender'],['age','gender'],[None]]
# #excluded = ['gender','age']
# for excluded in to_exclude:
# 	print "Excluding ", excluded

data= Orange.data.Table(sys.argv[1])
#print "using features: ", [feature.name for feature in data.domain if feature.name != excluded]
#new_domain = Orange.data.Domain([feature for feature in data.domain if feature.name not in excluded and feature is not data.domain.class_var], data.domain.class_var)
# And the new data table
#new_data = Orange.data.Table(new_domain, data)
tree = Orange.classification.tree.TreeLearner(m_pruning=True, m=2)
tree.name = "tree"
nbc = Orange.classification.bayes.NaiveLearner()
nbc.name = "nbc"
svm = Orange.classification.svm.SVMLearner()
svm.name = "svm"
knn = Orange.classification.knn.kNNLearner(k=5)
knn.name = 'knn'

learners = [tree, nbc, svm, knn]

print " "*9 + " ".join("%-4s" % learner.name for learner in learners)
res = Orange.evaluation.testing.cross_validation(learners, data, folds=10)
print "Accuracy %s" % " ".join("%.2f" % s for s in Orange.evaluation.scoring.CA(res))
print "AUC      %s" % " ".join("%.2f" % s for s in Orange.evaluation.scoring.AUC(res))

tree = Orange.classification.tree.TreeLearner(data)
#print tree.to_string()
tree.dot(file_name="tree.dot", node_shape="ellipse", leaf_shape="box")

# tree = Orange.classification.tree.TreeLearner(m_pruning=2, name="tree")
# boost = Orange.ensemble.boosting.BoostedLearner(tree, name="boost")
# bagg = Orange.ensemble.bagging.BaggedLearner(tree, name="bagg")

# learners = [tree, boost, bagg]
# results = Orange.evaluation.testing.cross_validation(learners, data, folds=20)
# for l, s in zip(learners, Orange.evaluation.scoring.AUC(results)):
#     print "%5s: %.2f" % (l.name, s)

# bayes = Orange.classification.bayes.NaiveLearner(name="bayes")
# tree = Orange.classification.tree.TreeLearner(name="tree")
# knn = Orange.classification.knn.kNNLearner(name="knn")

# base_learners = [bayes, tree, knn]
# stack = Orange.ensemble.stacking.StackedClassificationLearner(base_learners)

# learners = [stack, bayes, tree, knn]
# res = Orange.evaluation.testing.cross_validation(learners, data, 20)
# print "\n".join(["%8s: %5.3f" % (l.name, r) for r, l in zip(Orange.evaluation.scoring.AUC(res), learners)])