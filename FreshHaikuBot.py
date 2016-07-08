'''
This is the bot that searches comment streams for summons.

If a comment contains the text "FreshHaikuBot! Write me a haiku." it will run
the HaikuGenerator function and reply with a comment containing the generated
haiku.

Tyler Sullivan and Alex Hildreth

'''


import praw
from praw.helpers import comment_stream
from HaikuGenerator import generate_haiku

user_agent = "User-Agent: HaikuGen 0.1 (by /u/teefour)"

r = praw.Reddit(user_agent=user_agent)

r.login('FreshHaikuBot', 'fishsticks', disable_warning=True)
subreddit = 'all'

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
