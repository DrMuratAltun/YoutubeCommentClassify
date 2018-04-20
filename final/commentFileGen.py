from sys import argv
import csv
import random
from random import randint

# main
def main():
    
    # get comments and setup generated file
    commentsFile = open(argv[1], 'r')
    labelFile = open(argv[1][:-4] + "Labeled.txt", 'w')    

    csvReaderList = list(csv.reader(commentsFile))
    numComments = len(csvReaderList) - 1
    
    indexList = []

    # randomize comments
    for i in range(500):
        randNum = randint(1, numComments)
        while randNum in indexList:
            randNum = randint(1, numComments)
        indexList.append(randNum)

    # write to file
    n = 1
    for randomIndex in indexList:
    	labelFile.write("[]" + csvReaderList[randomIndex][0] + "\n\n")
        n = n + 1

    commentsFile.close()
    labelFile.close()

main()
