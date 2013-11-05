# A set of functions to read in our big MSE files and then get
# specific features from each series, including
# overall slope, first and second derivatives.  Note that all
# of these functions take as input a single MSE array, i.e.,
# a list of numbers where each successive number corresponds
# to an entropy value at a successively higher scale.


def get_inflection_point(mse_array):
    """
    Returns the x and y value
    of the point of the mse curve
    where the absolute value
    of the second derivative is 
    maximized.  This measure didn't seem
    to tell us much and was nearly always 
    at the first scale.  
    """
    import numpy as np

    # Get arrays w/ first and second derivatives of MSE curve at every scale
    second_derivative = np.diff(mse_array, 2)

    # Get the inflection points
    inflection_x = np.argmax(abs(second_derivative)) + 1  # find where second derivative is closest to zero
    inflection_y = mse_array[inflection_x]

    return inflection_x, inflection_y


def get_max_min_slope(mse_array):
    """
    Returns the minimum value,
    maximum value, and the overall/average
    slope from beginning to end of the input
    mse_array
    :param mse_array: an array of mse data
        organized by increasing scale
        (i.e., mse_array[0] is the entropy
        at the first scale, and mse_array[-1]
        is the entropy at the highest scale)
    """

    maximum = mse_array.max()
    minimum = mse_array.min()
    slope = float((mse_array[-1] - mse_array[0])) / mse_array.shape[0]
    mean = mse_array.mean()

    return minimum, maximum, slope, mean


def fit(mse_array, degree=3):
    """
    Returns the coefficients for
    a polynomial fit of the degree
    specified by the 'degree' argument.
    :param mse_array: an array of MSE values organized by scale
    :param degree: the degree of the polynomial to be fit. default = 3
    :rtype : object
        The returned numpy array contains the coefficients
        of the 'degree'-degree polynomial that is
        best fit to the data in mse_array.  The first
        element is the coefficient of the highest-degree
        term.
    """
    import numpy as np

    xData = range(len(mse_array))
    return np.polyfit(xData, mse_array, degree)








