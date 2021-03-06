#!/usr/bin/env python3

# Based on https://github.com/zwass/heroku-twitterbot-starter

import os
import sys
import time
import re
import random

import tweepy

from draw_medal import draw_medal

# DEBUG
TRACEABLE_MENTION = True
POST_TWEET = True  # Change to False for testing

TWEETS_TO_GRAB = 2  # Per justification

JUSTIFICATIONS = (
    'I DESERVE A MEDAL FOR ',
    'I SHOULD GET A MEDAL FOR ',
    'I DESERVE AN AWARD FOR ',
    'I SHOULD GET AN AWARD FOR '
)

REPLACEMENT_WORDS = tuple(zip("""
I'D
I'M
I
ME
MY
MYSELF
AM
""".strip().split(), """
THEY'D
THEY'RE
THEY
THEM
THEIR
THEMSELF
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
forbidden_words = os.environ.get('FORBIDDEN_WORDS').split('-')
forbidden_fragments = os.environ.get('FORBIDDEN_FRAGMENTS').split('-')

def log(s):
    pass
    # print(s)

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


def get_medal_text(status, q):

    # Ignore mentions (unless they're directly to @wdywam)
    if status.in_reply_to_user_id_str and not status.text.startswith('@wdywam'):
        log("INVALID (reply): " + status.text)
        return

    if 'RT' in status.text:
        log("INVALID (retweet): " + status.text)
        return

    if 'http' in status.text:
        log("INVALID (link): " + status.text)
        return

    for word in forbidden_fragments:
        if word in status.text:
            log("INVALID (forbidden term): " + status.text)
            return
    for word in forbidden_words:
        if re.match(r'''\b''' + word + r'''\b''', status.text):
            log("INVALID (forbidden term): " + status.text)
            return

    # Split by "I deserve a medal for..."
    try:
        throwaway, medal_text = status.text.upper().split(q)
    except ValueError:
        return

    if '@' in medal_text:
        log("INVALID (username): " + status.text)
        return

    # Decurlyfy
    medal_text = medal_text.replace('“','"').replace('”','"').replace('’', "'")

    # Replace I/ME/MY with THEY/THEM/THEIR
    for pair in REPLACEMENT_WORDS:
        medal_text = re.sub(r'''\b''' + pair[0] + r'''\b''', pair[1], medal_text)

    # Just get the rest of the sentence.
    medal_text = re.match(r'''[\w \+\-\'\"&$=@#,/]+''', medal_text).group(0)

    if len(medal_text) < 9:
        # log("INVALID (too short): " + status.text)
        return

    return {'medal_uname': status.user.screen_name,
            'medal_text': medal_text,
            'src_status': src_status.text}


if __name__ == "__main__":

    twapi = get_twapi()

    # Get ID of most recent tweet
    new_last_id = twapi.me().status.id  # Keep track of latest id found

    while True:  # Main loop

        last_id = new_last_id

        for search_q in JUSTIFICATIONS:
            src_statii = twapi.search(q='"' + search_q + '"',
                                      count=TWEETS_TO_GRAB,
                                      since_id=last_id)

            for src_status in src_statii:

                new_last_id = max(new_last_id, src_status.id)

                tweet = get_medal_text(src_status, q=search_q)
                if not tweet:
                    continue

                # Draw the medal
                tweet['fn'] = draw_medal(uname=tweet['medal_uname'],
                                         text=tweet['medal_text'])

                # Tweet the medal
                reply_uname = ('@'+tweet['medal_uname']) if TRACEABLE_MENTION else tweet['medal_uname']
                tweet['status'] = '{} {}{}'.format(random.choice(CONGRATS),
                                                      reply_uname,
                                                      random.choice('.!')
                                                      )
                if POST_TWEET:
                    twapi.update_with_media(filename=tweet['fn'],
                                            status=tweet['status'],
                                            in_reply_to_status_id=src_status.id)

                print('{}: {} => {}'.format(src_status.id,
                                                 tweet['src_status'],
                                                 tweet['status']))

        time.sleep(7200)  # 60 minutes
