"""
haiku generator v0.1
by Alex Hildreth and Tyler Sullivan

Using the PRAW library and CMU pronunciation dictionary, this script
parses the stream of current reddit comments for lines of 5 and 7 syllables.
These are then constructed into a haiku and displayed to the user.

ULTRA TEST EDIT
"""

import praw
from praw.helpers import comment_stream
from nltk.corpus import cmudict
import re
import csv
import os.path

user_agent = "User-Agent: HaikuGen 0.1 (by /u/teefour)"

r = praw.Reddit(user_agent=user_agent)

#r.set_oauth_app_info(client_id='VU5UkWmSxrKo8Q',
#                    client_secret='lEqInv-O7Hygig3y3dILtNYpYz8',

r.login('FreshHaikuBot', 'fishsticks', disable_warning=True)
# subreddit = 'all'



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
        for comment in comment_stream(r, 'all', limit=100):

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
                    # set the used flag
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

    # respond to comment with haiku
    theHaiku = lineOne + '\n\n' + lineTwo + '\n\n' + lineThree + '\n\n' + '***' +\
               '\n\n By: ' + str(authorOne.name) + ', ' + str(authorTwo.name) + \
               ', and ' + str(authorThree.name)


    """
    # print out the haiku
    print('***********************************************************')
    print('An original Reddit haiku:')
    print('')
    print(lineOne)
    print(lineTwo)
    print(lineThree)
    print('')
    print('By: /u/', authorOne.name, ', /u/', authorTwo.name, ', and /u/', authorThree.name)
    print('***********************************************************')
    """

    # appends haiku to csv file
    with open("haikus.csv", "a") as logfile:
        wr = csv.writer(logfile, delimiter=DELIM, lineterminator='\n')
        wr.writerow([lineOne, lineTwo, lineThree, authorOne, authorTwo, authorThree])
    return theHaiku

# wait for a user to summon the bot
while True:
    for comment in comment_stream(r, 'teefourpythontest', limit=1):
        if comment.body == "FreshHaikuBot! Write me a haiku.":
            haiku = generate_haiku()
            comment.reply(haiku)
            print(haiku)
