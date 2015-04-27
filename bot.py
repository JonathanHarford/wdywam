#!/usr/bin/env python

# Bsed on https://github.com/zwass/heroku-twitterbot-starter

import os
import sys
import time
import re
import random

import tweepy
from imgurpython import ImgurClient
from draw_medal import draw_medal

# DEBUG
UPLOAD_TO_IMGUR = True
TRACEABLE_MENTION = False
POST_TWEET = False


TWEETS_TO_GRAB = 5  # Per justification
last_id = 592449095043776512 # Keep track of latest id found

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
    'And the winner is... (opens envelope)',
    'Congrats,',
    'Here you go,',
    'Way to go,',
    'And the award goes to...',
    'Congratulations,',
    "I'm so proud of you,"
)

# These are for filtering out bad words. I couldn't bring myself to commit a file with such nastiness in
# it so I use environment variables instead.
forbidden_words = os.environ.get('FORBIDDEN_WORDS').split('-');
forbidden_fragments = os.environ.get('FORBIDDEN_FRAGMENTS').split('-');

def get_twapi():
    consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    if not all((consumer_key, consumer_secret, access_token, access_token_secret)):
        sys.exit("Environment variables not set.")
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

def get_medal_text(status, search_q):

    # Ignore mentions (unless they're directly to @wdywam)
    if status.in_reply_to_user_id_str and not status.text.startswith('@wdywam'):
        print("INVALID (reply): " + status.text)
        return

    if 'RT' in status.text:
        print("INVALID (retweet): " + status.text)
        return

    for word in forbidden_fragments:
        if word in status.text:
            print("INVALID (forbidden term): " + status.text)
            return
    for word in forbidden_words:
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

    return {'medal_uname': status.user.screen_name,
            'medal_text': medal_text,
            'src_status': src_status.text}


def imgur_upload_medal(path, uname, medal_text):
    client = ImgurClient(os.environ.get('IMGUR_CLIENT_ID'),
                         os.environ.get('IMGUR_SECRET'))

    config = {
        'title': 'A medal for ' + uname,
        'description': medal_text,
    }
    imgur_img = client.upload_from_path(path, config=config, anon=False)
    # print(imgur_img)
    return imgur_img

if __name__ == "__main__":

    twapi = get_twapi()

    while True:  # Main loop

        tweets = []

        # mentions = twapi.mentions_timeline(since_id=last_id)
        # for src_status in mentions:

        for search_q in JUSTIFICATIONS:
            src_statii = twapi.search(q='"' + search_q + '"',
                                      count=TWEETS_TO_GRAB,
                                      since_id=last_id)
            for src_status in src_statii:

                last_id = max(last_id, src_status.id)

                medal_data = get_medal_text(src_status, search_q=search_q)
                if not medal_data: continue

                medal_data['src_id'] = src_status.id

                # Draw the medal
                fn = draw_medal(uname=medal_data['medal_uname'],
                                text=medal_data['medal_text'])

                # Upload the medal
                if UPLOAD_TO_IMGUR:
                    imgur_data = imgur_upload_medal(fn,
                                                    uname=medal_data['medal_uname'],
                                                    medal_text=medal_data['medal_text'])
                    medal_data['deletehash'] = imgur_data['deletehash']
                    medal_data['link'] =  imgur_data['link']
                else:
                    medal_data['link'] = 'http://DEBUG.DEBUG/DEBUG'

                # Tweet the medal
                reply_uname = ('@'+medal_data['medal_uname']) if TRACEABLE_MENTION else medal_data['medal_uname']
                medal_data['status'] = '{} {}{} {}'.format(random.choice(CONGRATS),
                                                           reply_uname,
                                                           random.choice('.!'),
                                                           medal_data['link'])
                tweets.append(medal_data)

        # Post the tweets
        for tweet in tweets:
            # if POST_TWEET:
            #     twapi.update_status(status=tweet['status'])
            print(tweet['src_id'])
            print(tweet['src_status'])
            print(tweet['status'])
            print('')

        time.sleep(60)
