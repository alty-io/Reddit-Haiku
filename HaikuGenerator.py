"""
haiku generator v0.1
by Alex Hildreth

Using the PRAW library and CMU pronunciation dictionary, this script
parses the stream of current reddit comments for lines of 5 and 7 syllables.
These are then constructed into a haiku and displayed to the user.

"""


import praw
from praw.helpers import comment_stream
from nltk.corpus import cmudict
import re

user_agent = "User-Agent: HaikuGen 0.1 (by /u/teefour)"

r = praw.Reddit(user_agent=user_agent)

subreddit = 'all'

lineOneFlag = False
lineTwoFlag = False
lineThreeFlag = False

dictionary = cmudict.dict()


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
                lineOne = comment
                lineOneFlag = True
                authorOne = comment.author
            elif not lineThreeFlag:
                lineThree = comment
                lineThreeFlag = True
                authorThree = comment.author
        elif syl == 7:
            if not lineTwoFlag:
                lineTwo = comment
                lineTwoFlag = True
                authorTwo = comment.author

        # check if haiku is complete
        if lineOneFlag and lineTwoFlag and lineThreeFlag:
            break

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