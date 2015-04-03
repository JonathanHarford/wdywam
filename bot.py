#!/usr/bin/env python

import os
import sys
import time
import re
import random

import tweepy
from imgurpython import ImgurClient
from forbidden_words import FORBIDDEN_FRAGMENTS, FORBIDDEN_WORDS
from draw_medal import draw_medal

JUSTIFICATIONS = (
    'I DESERVE A MEDAL FOR ',
    'I DESERVE AN AWARD FOR ',
    'I SHOULD GET A MEDAL FOR ',
    'I SHOULD GET AN AWARD FOR ',
)

REPLACEMENT_WORDS = tuple(zip("""
I
ME
MY
AM
""".strip().split(), """
THEY
THEM
THEIR
ARE
""".strip().split()))

CONGRATS = (
    '(Opens envelope.)',
    'Congrats,',
    'Here you go,',
    'And the award goes to...',
    'Congratulations,',
    "I'm so proud of you,"
)

def get_medal_text(status, search_q):

    if status.in_reply_to_user_id_str:
        print("INVALID (reply): " + status.text)
        return

    if 'RT' in status.text:
        print("INVALID (retweet): " + status.text)
        return

    for word in FORBIDDEN_FRAGMENTS:
        if word in status.text:
            print("INVALID (forbidden term): " + status.text)
            return
    for word in FORBIDDEN_WORDS:
        if re.match(r'''\b''' + word + r'''\b''', status.text):
            print("INVALID (forbidden term): " + status.text)
            return

    # Split by "I deserve a medal for..."
    throwaway, medal_text = status.text.upper().split(search_q)

    # Replace I/ME/MY with THEY/THEM/THEIR
    for pair in REPLACEMENT_WORDS:
        medal_text = re.sub(r'''\b''' + pair[0] + r'''\b''', pair[1], medal_text)

    # Just get the rest of the sentence.
    medal_text = re.match(r'''[\w \+\-\'\"\&\$\=\@\#\,\/]+''', medal_text).group(0)

    if len(medal_text) < 9:
        print("INVALID (too short): " + status.text)
        return

    return {'medal_uname': status.user.screen_name, 'medal_text': medal_text}


def upload_medal(path):
    client = ImgurClient(os.environ.get('IMGUR_CLIENT_ID'),
                         os.environ.get('IMGUR_SECRET'))
    return client.upload_from_path(path)


if __name__ == "__main__":

    # Auth stuff
    consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    if not all((consumer_key, consumer_secret, access_token, access_token_secret)):
        sys.exit("Environment variables not set.")
    auth.set_access_token(access_token, access_token_secret)

    twapi = tweepy.API(auth)
    medals = []

    for search_q in JUSTIFICATIONS:
        src_statii = twapi.search(q='"' + search_q + '"', count=1)
        for src_status in src_statii:
            medal_data = get_medal_text(src_status, search_q=search_q)

            if medal_data:

                # Draw the medal
                fn = draw_medal(uname=medal_data['medal_uname'],
                                text=medal_data['medal_text'])
                #
                # # Upload the medal
                # imgur_data = upload_medal(fn)
                # medal_data.update({'deletehash': imgur_data['deletehash'],
                #                    'link': imgur_data['link']})
                medal_data['link'] = 'http://blah'

                # Tweet the medal
                status_text = '{} {}{} {}'.format(random.choice(CONGRATS),
                                                        '@' + medal_data['medal_uname'],
                                                        random.choice('.!'),
                                                        medal_data['link'])
                print('')
                print(src_status.text)
                # twapi.update_status(status=status_text)
                print(status_text)
                print(medal_data['medal_text'])
                print('')

    # twapi.update_status(status="Hello, World!")

    # while True:
    #     #Send a tweet here!
    #     time.sleep(60)
