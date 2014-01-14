__author__ = 'margaretsheridan'

#  I'm just trying to sketch out how I'm going to do some feature selection
#  through a number of different methods and then compare which features
#  are selected by those methods.


def rank_features_by_ttest(orangeDataTable, class1=None, class2=None):
    """
    Takes an Orange data table and returns
    a list of (feature name, p-value) tuples
    sorted in order of increasing p-value.
    The p-value is obtained through an independent
    samples t-test, using the class variable
    to divide the set into groups.  If no class
    arguments are provided, the first two class
    values in orangeDataTable.domain.class_var.values
    are used.

    It would be cool to be able to take more than
    two classes and compare between all pairs.

    :param class1: class
    :param class2:
    :param orangeDataTable:
    :rtype = list
    """
    import scipy.stats as stat
    import Orange.data

    # If the user didn't input a class, just use the first two class values of the input table
    if class1 is None:
        class1 = orangeDataTable.domain.class_var.values[0]
    if class2 is None:
        class2 = orangeDataTable.domain.class_var.values[1]

    # Initialize an empty list in which to store the (feature,score) tuples
    feature_scores = []

    # TODO: get only numerical features since a t-test can't be performed with nominal variables
    # This doesn't really matter for now for us since we only have continuous attributes

    # We can only do this on subjects who have defined class values filter out those who don't.
    # This shouldn't be a problem for correctness since the t-test looks for a specific
    # class value to group on, but there could be gains in efficiency if there are a large
    # number of instances without class information
    instances_with_class = Orange.data.filter.HasClassValue(orangeDataTable)

    # Create a filter to check whether values are defined.  Initially set the
    # check to zero for all attributes
    f = Orange.data.filter.IsDefined(domain=orangeDataTable.domain, check=[0 for attribute in orangeDataTable.domain])

    # Iterate over the features of the domain, each time performing an independent samples
    # t-test to compare group means for the given feature

    for feature in orangeDataTable.domain.features:
        f.check[feature] = 1  # Filter only based on current attribute

        _, prob = stat.ttest_ind(
            [dataInstance[feature] for dataInstance in f(instances_with_class) if dataInstance.get_class() == class1],
            [dataInstance[feature] for dataInstance in f(instances_with_class) if dataInstance.get_class() == class2])

        # Reset the filter
        f.check[feature] = 0

        # Add the (feature, p-value) tuple to the list
        feature_scores.append((feature.name, prob))

    # Return the list, sorted by increasing p-value
    return [feature for feature in sorted(feature_scores, key=lambda x: x[1])]


def rank_by_rfe(orangeDataTable, nFeatures, nFolds=10):
    """
    This function returns a list of
    (feature, SVM weight) tuples ranked
    in order of the SVM weights.  Since RFE
    is being used, the order of the ranking can vary
    for different feature set sizes (i.e, the
    top-ranked feature of the top 20 selected
    by RFE might not be the same as the top-ranked
    feature if RFE were used to select the top
    19 features).

    :rtype : list of tuples
    :param nFolds:
    :param orangeDataTable:
    :param nFeatures:
    """
    import Orange

    # Initialize a linear SVM learner
    svmLearner = Orange.classification.svm.SVMLearnerEasy(
        kernel_type=Orange.classification.svm.SVMLearnerEasy.Linear, folds=nFolds)

    # Reduce the domain of the input table using recursive feature elimination
    rfe = Orange.classification.svm.RFE(learner=svmLearner)
    rfe_data = rfe(orangeDataTable, nFeatures)

    # Get the linear weights of the SVM run on the top 20 features
    # so that they can be returned in ranked order.
    feature_weights = Orange.classification.svm.get_linear_svm_weights(svmLearner(rfe_data))

    # Unfortunately, this returns a linear weight for meta-attributes, so 'sID' for
    # our data set.  Since meta-attributes aren't included in the domain, we
    # return a list of rankings that only includes attributes included in the new domain.
    # The feature.name[2:] is used because Orange automatically prepends N_ to the
    # beginning of all the features in the new domain since they were normalized.

    return sorted([(feature.name[2:], weight) for (feature, weight) in feature_weights.items()
                   if feature.name[2:] in rfe_data.domain], key=lambda x: x[1], reverse=True)


def venn_diagram(**kwargs):
    """
    Takes sets as arguments
    and returns an effective
    Venn diagram

    :param **kwargs:  some number of sets
    """

    import itertools

    variations = {}
    for i in range(len(kwargs)):
        for combo in itertools.combinations(kwargs.keys(), i + 1):
            vsets = [kwargs[x] for x in combo]
            variations[tuple(sorted(combo))] = reduce(lambda x, y: x.intersection(y), vsets)

    return variations


def rank_by_GainRatio(table):
    """
    Takes as an argument an Orange data table
    object and returns a list of (feature, ranking)
    tuples, where the ranking is the Gain Ratio of
    the feature as calculated by Orange.

    :param table: an Orange data table
    :rtype:  list
    """

    import orange
    import Orange

    # Discretize the data using equal frequency discretization
    discrete_data = orange.Preprocessor_discretize(table, method=Orange.feature.discretization.EqualFreq(n=6))

    # Score the data using gain ratio
    ranked_features = Orange.feature.scoring.score_all(discrete_data, score=Orange.feature.scoring.GainRatio())

    # Remove the D_ that's automatically prepended to the feature names when they're discretized
    return [(i[2:], j) for (i, j) in ranked_features]


def compare_features(table, nFeatures):
    """
    Uses the ranking functions
    and transforms the
    outputs from lists of (feature, score)
    tuples to sets of just feature names

    :param table: an Orange data table
    :param nFeatures: the number of top features to
        compare from each method
    """

    # Get just the names of the top nFeatures features via each scoring method
    top_by_ttest = set([x[0] for x in rank_features_by_ttest(table)[:nFeatures]])
    top_by_RFE = set([y[0] for y in rank_by_rfe(table, nFeatures)])
    top_by_GR = set([z[0] for z in rank_by_GainRatio(table)[:nFeatures]])

    # Make make the "Venn diagram", which is just a dictionary
    # that fully describes features shared by different combinations
    # of the feature selection techniques.
    return venn_diagram(t=top_by_ttest, RFE=top_by_RFE, GR=top_by_GR)


def print_venn_diagram(a, b, c):
    """
    prints a Venn diagram
    from sets a, b, and c
    """
    # Make the Venn diagram first

    # Unique to one set
    just_a = list(a.difference(b.union(c)))
    just_b = list(b.difference(c.union(a)))
    just_c = list(c.difference(b.union(a)))

    # Uniquely shared by two sets
    just_a_and_b = list(a.intersection(b).difference(c))
    just_b_and_c = list(b.intersection(c).difference(a))
    just_a_and_c = list(c.intersection(a).difference(b))

    # The intersection of all three sets
    a_and_b_and_c = list(a.intersection(b).intersection(c))

    print "TOP"
    for i in range(max(map(len, [just_a, just_a_and_b, just_b]))):
        print_if_possible(just_a, i)
        #  print "\t\t",
        print_if_possible(just_a_and_b, i)
        # print "\t\t",
        print_if_possible(just_b, i)
        print "\n",
    print "MIDDLE"
    for i in range(max(map(len, [just_a_and_c, just_b_and_c, a_and_b_and_c]))):
    # print "\t",
        print_if_possible(just_a_and_c, i)
        # print "\t",
        print_if_possible(a_and_b_and_c, i)
        #  print "\t",
        print_if_possible(just_b_and_c, i)
        print "\n",
    print "BOTTOM"
    for i in range(len(just_c)):
        print_if_possible(just_c, i)
        print "\n",


        #TODO:  make this into an actual function that will either return the things I need
        #TODO:  to put into a venn diagram, or to actually print an ASCII venn diagram.


def print_if_possible(some_list, index):
    """
    prints some_list[index]
    If index is less than
    len(some_list), otherwise
    does nothing.

    :param some_list:
    :param index:
    """
    try:
        print "%-30s" % some_list[index],

    except IndexError:
        print "%-30s" % ''
