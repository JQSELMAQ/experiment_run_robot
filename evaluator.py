import re
import json
import requests
import os
import wget
from Levenshtein import lev
evaluation_list = []
madestring = ""
corrected_string = ""
numberlist = []
M_test_dict = {}
iterate2 = 0
iterate3 = 0
iterate4 = 0
iterate5 = 0
nato_list = ['ALPHA', 'BRAVO', 'CHARLIE', 'DELTA', 'ECHO', 'FOXTROT', 'GOLF', 'HOTEL', 'INDIA', 'JULIET', 'KILO',
             'LIMA',
             'MIKE', 'NOVEMBER', 'OSCAR', 'PAPA', 'QUEBEC', 'ROMEO', 'SIERRA', 'TANGO', 'UNIFORM', 'VICTOR', 'WHISKEY',
             'X-RAY', 'YANKEE', 'ZULU', "Recording license plate", "Reporting license plate", "recording license plate", "reporting license plate"]
for x in range(0, 101):
    x = str(x)
    nato_list.append(x)
    x = int(x)
    x += 1

with open('Mike.txt') as Mike:  # Future nato-alphabet checking dictionary
    Mikelist = Mike.readlines()
    for items in Mikelist:
        Mikelist[iterate4] = Mikelist[iterate4].strip()
        iterate4 += 1

for entries in Mikelist:
    M_test_dict[entries] = 'Mike'


def evaluate(inputs):
    global iterate2, evaluation_list, madestring, iterate3, iterate5, corrected_string
    for words in inputs.split():
        listwords = inputs.upper().split()
        if listwords[iterate2] not in nato_list:
            if listwords[iterate2] in M_test_dict:
                print("Replacing", listwords[iterate2], "with identified match MIKE.\n\n")
                listwords[iterate2] = M_test_dict[listwords[iterate2]].upper()
                corrected_string = str(listwords[iterate2])
        listword = list(listwords[iterate2])
        if listword[0].isdigit():
            shorten = listwords[iterate2]
            shorten = re.sub(":", '', shorten)
            shorten = re.sub("/", '', shorten)
            evaluation_list.append(shorten)
        else:
            evaluation_list.append(listword[0])

        iterate2 += 1
    iterate2 = 0
    for items in evaluation_list:
        madestring += str(evaluation_list[iterate3])
        iterate3 += 1
    iterate3 = 0
    returnstring = madestring.upper()
    madestring = ""
    corrected_string = ""
    evaluation_list = []
    return returnstring
