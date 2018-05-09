import pandas as pd 
from pprint import pprint
import numpy, sys, tqdm, random
from sklearn.metrics import mean_squared_error

pd.set_option('expand_frame_repr', False)

MAX_HEIGHT = 4



class Utils(object):

	def __init__(self, path, targets):
		self.dataset = pd.read_csv(filepath_or_buffer = path, header = 'infer')
		self.target = targets
		self.columnlist = ["CompPrice",  "Income",  "Advertising",  "Population",  "Price",  "Age", "Education"]
		self.alpha = 0.25
		self.height = 1
		self.bestSplits = list()
		self.path = []
		self.leaves = []

	def process (self, training_set_size):
		# edge case -- 1
		if training_set_size > 1:
			training_set_size = training_set_size / 100

		# randomly shuffle all rows
		self.dataset = self.dataset.sample(frac = 1)
		# split train : test :: training_set_size : 1 - training_set_size ratio
		train_dataset, test_data = numpy.split(self.dataset, [int(len(self.dataset) * training_set_size)])
		# train_targets, test_targets = train_dataset.pop('Sales'), test_data.pop('Sales')
		return train_dataset, test_data

	computeTarget = lambda self, chunk : chunk[self.target].median()
	regularize = lambda self, data : self.computeRSS(data) + (self.alpha * len(data.columns.tolist()))

	def performSplit (self, train_data, feature):
		return train_data[train_data[feature] > train_data[feature].mean()], train_data[train_data[feature] < train_data[feature].mean()]

	# pick min value out of this. 
	def computeRSS (self, chunk):
		# (true of each entry in chunk - median of chunk) ** 2
		rss = 0.0
		predicted_target = self.computeTarget(chunk)
		for index, row in chunk.iterrows():
			rss += numpy.power((row[self.target] - predicted_target), 2)
		return rss

	computeMSE = lambda self, actual, pred : mean_squared_error(actual, pred)
	pathTraversed = lambda self : self.bestSplits

	def recursiveSplit (self, chunk):

		self.height += 1
		# define stopping conditions
		if chunk.shape[0] < (0.10 * self.dataset.shape[0]):

			self.leaves.append(self.computeTarget(chunk))
			return 0

		if self.height == MAX_HEIGHT:

			self.leaves.append(self.computeTarget(chunk))
			return 0


		combinedRss = []
		nodes = []
		for feature in self.columnlist:
			chunk1, chunk2 = self.performSplit(chunk, feature)
			rss = self.computeRSS(chunk1) + self.computeRSS(chunk2)
			combinedRss.append(rss)
			single_node = node(chunk1, chunk2, feature)
			nodes.append(single_node)

		# returns the split with lowest RSS value. 
		min_rss = numpy.argmin(combinedRss)
		# nodes[min_rss].printNodeFeature()
		self.bestSplits.append(nodes[min_rss].getSplitFeature())
		print("At level {}, the least RSS is for split at : {}".format(self.height, nodes[min_rss].getSplitFeature()))
		self.recursiveSplit(nodes[min_rss].getLeft())
		self.recursiveSplit(nodes[min_rss].getRight())
		return self.bestSplits, self.leaves

	




class node(object):
	def __init__(self, left, right, feature):
		self.splitVal = feature
		self.left = left
		self.right = right
	def getLeft(self):
		return self.left
	def getRight(self):
		return self.right
	def setLeft(self, chunk):
		self.left = chunk
	def setRight(self, chunk):
		self.right = chunk
	def setSplitFeature (self, feature):
		self.splitVal = feature
	def getSplitFeature (self):
		return self.splitVal
	def printNodeFeature(self):
		print(self.splitVal)



def main ():

	# read user input for the dataset
	DATASET = sys.argv[1]

	# Create an object for the Utils class with dataset path and target to predict. 
	util = Utils(DATASET, 'Sales')
	train, test = util.process(0.8)
	path, leaves = util.recursiveSplit(train)
	# pprint(util.pathTraversed())
	pprint(leaves)

		
if __name__ == '__main__':
	main()

