"""
    This script is reading data from input.csv and printing to output.txt the following: Amount of Numbers & Average
    this is done with the csv library

    Author: Andrei-Antonio Robu (andrei-antonio.robu@student.tuiasi.ro)
"""
import csv
from statistics import mean

# testing

if __name__ == '__main__':
    with open('input.csv', newline='\n') as csvfile:
        spamreader = csv.reader(csvfile)
        fOut = open('outputCSV.txt', 'wt')
        fOut.write("Amount of no\tAverage")
        for row in spamreader:
            fOut.write('\n')
            fOut.write(str(len(row)))
            for i in range(len(row)):
                if row[i].__contains__('.') : row[i]=float(row[i])
                else: row[i]=float(row[i])
            fOut.write('\t\t\t\t{}'.format(str(mean(row))))
