def plot_trajectory(inFileName):

	import matplotlib.pyplot as plt
	import json

	# Set labels
	PLOT_TITLE = "Linear SVM Classification Accuracy vs Feature Set Size"
	X_LABEL = "Feature Set Size"
	Y_LABEL = "Classification Accuracy"

	with open(inFileName,"rb") as inFile:
		size_info = json.load(inFile)
		
	set_sizes = [i[0] for i in size_info[1:]]
	accuracy = [i[1] for i in size_info[1:]]

	# Plot classification accuracy vs feature set size
	RFE_plot = plt.plot(set_sizes, accuracy)

	# Add title and label axes
	plt.title(PLOT_TITLE)
	plt.xlabel(X_LABEL)
	plt.ylabel(Y_LABEL)

	# Display the plot
	plt.show()
		

if __name__ == "__main__":
	import sys
	plot_trajectory(sys.argv[1])
	

