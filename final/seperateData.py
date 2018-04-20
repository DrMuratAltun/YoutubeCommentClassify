import os

# seperate comments in files
def makeFiles(liked, disliked):
	positiveFile = open("positive/likedComments.txt", "w")
	negativeFile = open("negative/dislikedComments.txt", "w")
	otherFile = open("other/otherComments.txt", "w")
	likedComments = liked.split('[')
	dislikedComments = disliked.split('[');
	for comment in likedComments:
		if (len(comment) > 1):
			if (comment[0] == 'P'):
				positiveFile.write("[" + comment)
			elif (comment[0] == 'N'):
				negativeFile.write("[" + comment)
			elif (comment[0] == 'O'):
				otherFile.write("[" + comment)

	for comment in dislikedComments:
		if (len(comment) > 1):
			if (comment[0] == 'P'):
				positiveFile.write("[" + comment)
			elif (comment[0] == 'N'):
				negativeFile.write("[" + comment)
			elif (comment[0] == 'O'):
				otherFile.write("[" + comment)
	positiveFile.close()
	negativeFile.close()
	otherFile.close()


# seperate each comment into their own files
def createDirectories():	
	positiveFile = open("positive/likedComments.txt", "r").read()
	negativeFile = open("negative/dislikedComments.txt", "r").read()
	otherFile = open("other/otherComments.txt", "r").read()
	os.remove("positive/likedComments.txt")
	os.remove("negative/dislikedComments.txt")
	os.remove("other/otherComments.txt")

	positives = positiveFile.split("[P]")
	negatives = negativeFile.split("[N]")
	others = otherFile.split("[O]")
	for i in range(1, len(positives)):
		comment = positives[i]
		newFile = open("positive/positive" + str(i) + ".txt", "w")
		newFile.write(comment)
		newFile.close()
	for i in range(1, len(negatives)):
        	comment = negatives[i]
        	newFile = open("negative/negative" + str(i) + ".txt", "w")
        	newFile.write(comment)
        	newFile.close()
	for i in range(1, len(others)):
		comment = others[i]
		newFile = open("other/other" + str(i) + ".txt", "w")
		newFile.write(comment)
		newFile.close()


# Main
def main():
	os.makedirs("negative")
	os.makedirs("positive")
	os.makedirs("other")
	currFile = open("likedLabeled.txt", "r")
	likedFile = currFile.read()
	currFile = open("dislikedLabeled.txt", "r")
	dislikedFile = currFile.read()
	currFile.close()
	makeFiles(likedFile, dislikedFile)
	createDirectories()
main()
