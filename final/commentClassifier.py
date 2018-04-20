from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
import os
import re
from nltk.stem.lancaster import LancasterStemmer
import sklearn.metrics
wordDict = {}
		

# generate negation
def genNegation():
	negWords = {"no", "not", "nothing", "never", "neither"}
	return negWords

# split apart data using fivefold cross validation
def chunkList(fileNames, size):
	newList = [[], [], [], [], []]
	index = 0
	listIndex = 0
	while (index < len(fileNames)):
		newList[listIndex].append(fileNames[index])
		if ((index + 1) % size == 0) and (listIndex != 4):
			listIndex = listIndex + 1
		index = index + 1
	return(newList)
		
# preprocess all data
def processing(fileDict):
	stemmer = LancasterStemmer()
	expandedWords = {}
	expandedWords["omg"] = "oh my god"
	expandedWords["wtf"] = "what the fuck"
	expandedWords["lol"] = "laughing out loud"
	expandedWords["lmao"] = "laughing my ass off"
	expandedWords["stfu"] = "shut the fuck up"
	expandedWords["nvm"] = "nevermind"
	expandedWords["bull"] = "bullshit"
	expandedWords["tf"] = "the fuck"
	expandedWords["bs"] = "bullshit"
	negWords = genNegation()
	negCounter = 0
	currNeg = False
	for name in fileDict:
		newComment = ""
		comment = fileDict[name]
		splitComments = comment.split(" ")
		for word in splitComments:
			word = removeSequence(word)
			currNeg = False
			sub = word[-3:].lower()
			if (word.lower() in negWords) or ("n't" == sub):
				currNeg = True		
				negCounter = 3
			word = re.sub('\W+', '', word)
			if (word in expandedWords):
				word = expandedWords[word]
			try:
				word = stemmer.stem(word)
			except:
				continue
			if (negCounter > 0) and (currNeg == False):
				word = "not_" + word
				negCounter = negCounter - 1
			newComment = newComment + str(word) + " "
		newComment = newComment[:-1]
		fileDict[name] = newComment
	return fileDict

# truncate repeated character sequences
def removeSequence(word):
	seqLen = 1
	prevChar = '';
	newWord = ""

	for c in word:
		if prevChar != '':
			if c == prevChar:
				seqLen = seqLen + 1;
			else:		
				seqLen = 1
		prevChar = c
		if seqLen <= 3:
			newWord = newWord + c

	return newWord

# map file name to its comment
def fillDictionary(posList, negList, otherList):
	fileDict = {}
	count = 0
	for i in range(0, len(posList)):
		files = str(posList[i])
		files = files.split(" ")
		for fileName in files:
			if (len(fileName) < 3):
				continue
			count = count + 1
			if (fileName[0] == '['):
				fileName = fileName[1:]
			if (fileName[-1] == ']'):
				fileName = fileName[:-1]
			fileName = fileName[1:]
			fileName = fileName[:-2]
			if (fileName[-1] != 't'): 
				fileName = fileName + 't'
			fileSplit = fileName.split(".txt")
			fileSplit = fileSplit[0].split("positive")
			currFile = open("positive/positive" + fileSplit[1] + ".txt", "r").read()
			fileDict[fileName] = currFile

	for i in range(0, len(negList)):
		files = str(negList[i])
		files = files.split(" ")
		for fileName in files:
			if (len(fileName) == 2):
				continue
			count = count + 1
			if (fileName[0] == '['):
				fileName = fileName[1:]
			if (fileName[-1] == ']'):
				fileName = fileName[:-1]
			fileName = fileName[1:]
			fileName = fileName[:-2]
			if (fileName[-1] != 't'):
				fileName = fileName + 't'
			fileSplit = fileName.split(".txt")
			fileSplit = fileSplit[0].split("negative")
			currFile = open("negative/negative" + fileSplit[1] + ".txt", "r").read()
			fileDict[fileName] = currFile
	for i in range(0, len(otherList)):
		count = count + 1
		files = str(otherList[i])
		files = files.split(" ")
		for fileName in files:
			if (len(fileName) == 2):
				continue
			count = count + 1
			if (fileName[0] == '['):
				fileName = fileName[1:]
			if (fileName[-1] == ']'):
				fileName = fileName[:-1]
			fileName = fileName[1:]
			fileName = fileName[:-2]
			if (fileName[-1] != 't'):
				fileName = fileName + 't'
			fileSplit = fileName.split(".txt")
			fileSplit = fileSplit[0].split("other")
			currFile = open("other/other" + fileSplit[1] + ".txt", "r").read()
			fileDict[fileName] = currFile
	return fileDict

# train and test classification
def classify(iteration, fileDict, posList, negList, otherList):
	trainingFiles = []
	trainingData = []
	trainingLabels = []
	testFiles = []
	testData = []
	testLabels = []

	# seperate test and training Data by names of the files
	for i in range(0, 5):
		if (i == iteration):
			if (len(posList[iteration]) > 0):
				testFiles.append(posList[iteration])
			if (len(negList[iteration]) > 0):			
				testFiles.append(negList[iteration])
			if (len(otherList[iteration]) > 0):
				testFiles.append(otherList[iteration])
		else:
			if (len(posList[i]) > 0):
				trainingFiles.append(posList[i])
			if (len(negList[i]) > 0):
				trainingFiles.append(negList[i])
			if (len(otherList[i]) > 0):
				trainingFiles.append(otherList[i])
	
	# Record labels
	for group in trainingFiles:
		for i in range(0, len(group)):
			name = group[i]
			if ("pos" in name):
				trainingLabels.append("P")
			elif ("neg" in name):
				trainingLabels.append("N")
			elif ("other" in name):
				trainingLabels.append("O")
			trainingData.append(fileDict[name])
		
	for group in testFiles:
		for name in group:
			if ("pos" in name):
				testLabels.append("P")
			elif ("neg" in name):
				testLabels.append("N")
			elif ("other" in name):
				testLabels.append("O")
			testData.append(fileDict[name])

	# train and test
	vectorizer = TfidfVectorizer(ngram_range = (1, 5), sublinear_tf = False, use_idf = True, stop_words = "english", lowercase = False)
	trainingVector = vectorizer.fit_transform(trainingData, trainingLabels)
	testVector = vectorizer.transform(testData)


	model = svm.SVC(kernel="linear")
	model.fit(trainingVector, trainingLabels)
	results = model.predict(testVector)
	overall = len(testLabels)
	correctPos = 0
	posNeg = 0
	posOth = 0
	correctNeg = 0
	negPos = 0
	negOth = 0
	correctOth = 0
	othPos = 0
	othNeg = 0

	# evaluate predictions
	for i in range(0, overall):
		currLabel = results[i]
		correctLabel = testLabels[i]
		if (currLabel == "P"):
			if (currLabel == correctLabel):
				correctPos = correctPos + 1
			else:
				if (correctLabel == "N"):
					posNeg = posNeg + 1
				elif (correctLabel == "O"):
					posOth = posOth + 1
		elif (currLabel == "N"):
			if (currLabel == correctLabel):
				correctNeg = correctNeg + 1
			else:
				if (correctLabel == "P"):
					negPos = negPos + 1
				elif (correctLabel == "O"):
					negOth = negOth + 1
		elif (currLabel == "O"):
			if (currLabel == correctLabel):
				correctOth = correctOth + 1
			else:
				if (correctLabel == "P"):
					othPos = othPos + 1
				elif (correctLabel == "N"):
					othNeg = othNeg + 1
	
	precisionP = correctPos / (correctPos + posNeg + posOth)
	recallP = correctPos / (correctPos + negPos + othPos)
	fscoreP = (2 * ((precisionP * recallP) / (precisionP + recallP)))
	precisionN = correctNeg / (correctNeg + negPos + negOth)
	recallN = correctNeg / (correctNeg + posNeg + othNeg)
	fscoreN = (2 * ((precisionN * recallN) / (precisionN + recallN)))
	precisionO = correctOth / (correctOth + othPos + othNeg)
	recallO = correctOth / (correctOth + posOth + negOth)
	fscoreO = (2 * ((precisionO * recallO) / (precisionO + recallO)))

	stats = [precisionP, recallP, fscoreP, precisionN, recallN, fscoreN, precisionO, recallO, fscoreO]
	print("Iteration " + str(iteration + 1))
	print("================================================================")
	print("================================================================")
	print("================================================================")
	print("Positive Precision : " + str(100 * precisionP) + "%")
	print("Positive Recall    : " + str(100 * recallP) + "%")
	print("Positive F-Score   : " + str(100 * fscoreP) + "%")
	print("Negative Precision : " + str(100 * precisionN) + "%")
	print("Negative Recall    : " + str(100 * recallN) + "%")
	print("Negative F-Score   : " + str(100 * fscoreN) + "%")
	print("Other Precision    : " + str(100 * precisionO) + "%")
	print("Other Recall       : " + str(100 * recallO) + "%")
	print("Other F-Score      : " + str(100 * fscoreO) + "%")
	print("Average Precision  : " + str(100 * (precisionP + precisionN + precisionO) / 3) + "%")
	print("Average Recall     : " + str(100 * (recallP + recallN + recallO) / 3) + "%")
	print("Average F-Score    : " + str(100 * (fscoreP + fscoreN + fscoreO) / 3) + "%")
	return stats

# main
def main():
	positiveFiles = os.listdir("positive/")
	negativeFiles = os.listdir("negative/")
	otherFiles = os.listdir("other/")
	positiveChunk = int((len(positiveFiles) / 5))
	negativeChunk = int((len(negativeFiles) / 5))
	otherChunk = int((len(otherFiles) / 5))
	positiveList = chunkList(positiveFiles, positiveChunk)
	negativeList = chunkList(negativeFiles, negativeChunk)
	otherList = chunkList(otherFiles, otherChunk)
	fileDict = fillDictionary(positiveList, negativeList, otherList)
	fileDict = processing(fileDict)
	sumList = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]	
	
	# test and train 5 times, and average the scores
	for i in range(0, 5):
		sumAccuracy = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
		sumAccuracy = classify(i, fileDict, positiveList, negativeList, otherList)
		for i in range(0, len(sumList)):
			sumList[i] = sumList[i] + sumAccuracy[i]
		wordDict = {}
		print("")
	print("")
	print("---------------------------------------------------------------------------")
	print("")
	print("")
	print("Average Positive Precision  : " + str(100 * (sumList[0] / 5)) + "%")
	print("Average Positive Recall     : " + str(100 * (sumList[1] / 5)) + "%")
	print("Average Positive F-Score    : " + str(100 * (sumList[2] / 5)) + "%")
	print("Average Negative Precision  : " + str(100 * (sumList[3] / 5)) + "%")
	print("Average Negative Recall     : " + str(100 * (sumList[4] / 5)) + "%")
	print("Average Negative F-Score    : " + str(100 * (sumList[5] / 5)) + "%")
	print("Average Other Precision     : " + str(100 * (sumList[6] / 5)) + "%")
	print("Average Other Recall        : " + str(100 * (sumList[7] / 5)) + "%")
	print("Average Other F-Score       : " + str(100 * (sumList[8] / 5)) + "%")
	print("Average Precision           : " + str(100 * ((sumList[0] + sumList[3] + sumList[6]) / 15)) + "%")
	print("Average Recall              : " + str(100 * ((sumList[1] + sumList[4] + sumList[7]) / 15)) + "%")
	print("Average F-Score             : " + str(100 * ((sumList[2] + sumList[5] + sumList[8]) / 15)) + "%")


main()
