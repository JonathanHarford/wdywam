#!/usr/bin/env python

import os
import sys
import time
import re
import random

import tweepy
from imgurpython import ImgurClient
from draw_medal import draw_medal

CONGRATS = (
    '(Opens envelope.)',
    'Congrats,',
    'Here you go,',
    'And the award goes to...',
    'Congratulations,',
    "I'm so proud of you,"
)

#### Tweepy Status object:
# {
#  'contributors': None,
#  'truncated': False,
#  'text': 'My Top Followers in 2010: @tkang1 @serin23 @uhrunland @aliassculptor @kor0307 @yunki62. Find yours @ http://mytopfollowersin2010.com',
#  'in_reply_to_status_id': None,
#  'id': 21041793667694593,
#  '_api': <tweepy.api.api object="" at="" 0x6bebc50="">,
#  'author': <tweepy.models.user object="" at="" 0x6c16610="">,
#  'retweeted': False,
#  'coordinates': None,
#  'source': 'My Top Followers in 2010',
#  'in_reply_to_screen_name': None,
#  'id_str': '21041793667694593',
#  'retweet_count': 0,
#  'in_reply_to_user_id': None,
#  'favorited': False,
#  'retweeted_status': <tweepy.models.status object="" at="" 0xb2b5190="">,
#  'source_url': 'http://mytopfollowersin2010.com',
#  'user': <tweepy.models.user object="" at="" 0x6c16610="">,
#  'geo': None,
#  'in_reply_to_user_id_str': None,
#  'created_at': datetime.datetime(2011, 1, 1, 3, 15, 29),
#  'in_reply_to_status_id_str': None,
#  'place': None
# }


def get_medal_text(status, search_q, first_person):

    # We don't want replies
    if status.in_reply_to_user_id_str:
        return

    # We don't want Retweets
    if 'RT' in status.text:
        return

    # Split by "I deserve a medal for..."
    throwaway, medal_text = status.text.upper().split(search_q)

    if first_person:
        # We don't want "Toni should get a medal for..."
        if not throwaway.endswith(' ') and len(throwaway) > 0:
            return

    # medal_text = medal_text.replace('\n','.')
    medal_text = re.match(r'''[\w \+\-\'\&\$\=\@]+''', medal_text).group(0)

    # Suspiciously short.
    if len(medal_text) < 9:
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
        print(consumer_key, consumer_secret, access_token, access_token_secret)
        sys.exit("Environment variables not set.")
    auth.set_access_token(access_token, access_token_secret)

    twapi = tweepy.API(auth)
    medals = []

    for search_q in ('I DESERVE A MEDAL FOR ', 'I DESERVE AN AWARD FOR ',
              'I SHOULD GET A MEDAL FOR ', 'I SHOULD GET AN AWARD FOR '):
        # statii = twapi.search(q='"' + search_q + '"', count=15)
        statii = twapi.search(q='"' + search_q + '"', count=1)
        for status in statii:
            medal_data = get_medal_text(status, search_q=search_q, first_person=True)
            if medal_data:
                # print(medal_data[0] + ': ' + status.text)
                # print('{} {}{} {}'.format(random.choice(CONGRATS),
                #                         medal_data[0],
                #                         random.choice('.!'),
                #                         'http://imgur.com/blah'))
                # print(medal_data[1])
                # print()

                fn = draw_medal(uname=medal_data['medal_uname'],
                                text=medal_data['medal_text'])
                imgur_data = upload_medal(fn)
                medal_data.update({'deletehash': imgur_data['delete_hash'],
                                   'link': imgur_data['link']})
                print(medal_data)
                medals.append(medal_data)

    # twapi.update_status(status="Hello, World!")

    # while True:
    #     #Send a tweet here!
    #     time.sleep(60)
