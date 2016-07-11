"""
haiku generator v0.2
by Alex Hildreth and Tyler Sullivan

Using the PRAW library and CMU pronunciation dictionary (part of NLTK), this script
parses the stream of current reddit comments for lines of 5 and 7 syllables.
These are then constructed into a haiku and displayed to the user.

This version has bot capabilities. It scans the current comment stream so a user
may call the bod from anywhere in reddit, and the bot will respond with a haiku.

"""

import praw
from praw.helpers import comment_stream
from nltk.corpus import cmudict
import re
import csv
import os.path

user_agent = "User-Agent: HaikuGen 0.2 (by /u/FreshHaikuBot)"

r = praw.Reddit(user_agent=user_agent)
subreddit = 'all'

# create a haiku on demand
def generate_haiku():
    lineOneFlag = False
    lineTwoFlag = False
    lineThreeFlag = False

    dictionary = cmudict.dict()

    DELIM=','
    # sets up csv file if it doesn't already exist for saving haikus
    fieldnames = ['lineOne', 'lineTwo', 'lineThree', 'authorOne', 'authorTwo', 'authorThree']
    if not os.path.isfile("haikus.csv"):
        with open("haikus.csv", "w") as logfile:
            wr = csv.writer(logfile, delimiter=DELIM, lineterminator='\n')
            wr.writerow(fieldnames)

    # checks if a string passed to it is a legitimate single letter word
    def single_check(char):
        if char == 'i' or char == 'a':
            return True
        else:
            return False

    # get comment stream until all haiku lines are filled
    while not lineOneFlag or not lineTwoFlag or not lineThreeFlag:
        for comment in comment_stream(r, subreddit, limit=100):

            # reset syllable count
            syl = 0

            # immediately pass if longer than 35 chars
            if len(comment.body) >= 35:
                continue

            # immediately pass if contains any digits
            if any(letter.isdigit() for letter in comment.body):
                continue

            # immediately pass if there is a new line in comment
            if any(letter == "\n" for letter in comment.body):
                continue

            # immediately pass if there is a "'", because it seems to confuse dictionary
            if any(letter == "'" for letter in comment.body):
                continue

            # split comment into a list of words without punctuation
            commentList = re.sub("[^\w]", " ", comment.body).split()

            # check if any word is not in the dictionary, if not pass to next comment
            if any(not word.lower() in dictionary for word in commentList):
                continue

            # cycle through list to get word syllables
            for word in commentList:

                # reset used flag, making sure word isn't counted for multiple pronunciations
                usedFlag = False

                # if word is single letter, check if "a" or "i"
                if len(word) == 1 and not single_check(word):
                    break

                # pull the dict definition and count the syllables
                definition = dictionary[word.lower()]
                for item in definition:
                    for char in item:
                        if any(letter.isdigit() for letter in char) and not usedFlag:
                            syl += 1
                            """ for testing:
                            print('comment: ', comment)
                            print('comment list: ', commentList)
                            print('item: ', item)
                            print('char: ', char)
                            print('syl count: ', syl)
                            """
                    # set the used flag so it doesn't count syllables in multiple entries
                    usedFlag = True

            # check for matching syllable counts and fill in lines
            if syl == 5:
                if not lineOneFlag:
                    lineOne = comment.body
                    lineOneFlag = True
                    authorOne = comment.author
                elif not lineThreeFlag:
                    lineThree = comment.body
                    lineThreeFlag = True
                    authorThree = comment.author
            elif syl == 7:
                if not lineTwoFlag:
                    lineTwo = comment.body
                    lineTwoFlag = True
                    authorTwo = comment.author

            # check if haiku is complete
            if lineOneFlag and lineTwoFlag and lineThreeFlag:
                break

    # construct haiku string to return
    theHaiku = lineOne + '\n\n' + lineTwo + '\n\n' + lineThree + '\n\n' + '***' +\
               '\n\n By: ' + str(authorOne.name) + ', ' + str(authorTwo.name) + \
               ', and ' + str(authorThree.name) + '\n\n I am a bot. This Haiku was ' + \
               'constructed from comments on the /r/all stream.\n\n If a line contained ' +\
               'too many syllables, please PM me so I can get better!'

    # appends haiku to csv file
    with open("haikus.csv", "a") as logfile:
        wr = csv.writer(logfile, delimiter=DELIM, lineterminator='\n')
        wr.writerow([lineOne, lineTwo, lineThree, authorOne, authorTwo, authorThree])
    return theHaiku

# leave this in to function as a generator without bot function
haiku = generate_haiku()
print(haiku)

"""
# leave this in to function as a reddit bot
# wait for a user to summon the bot
while True:
    for comment in comment_stream(r, subreddit, limit=100):
        # if comment.body == "FreshHaikuBot! Write me a haiku.":
        if "FreshHaikuBot! Write me a haiku." in comment.body:
            # print to console to know its working
            print('\n*****************************')
            print('request received. Working...')
            print('*****************************\n')

            # get a haiku
            haiku = generate_haiku()

            # send the haiku to the requester and print it to console
            comment.reply(haiku)
            print(haiku)
"""
