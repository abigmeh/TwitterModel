from __future__ import print_function

from collections import Counter

import tweepy
import json
from pymongo import MongoClient
import numpy as np
import re
import utilities
import pandas as pd
import datetime
from tweepy import Cursor

pd.set_option('display.max_columns', 7)
pd.set_option('display.width', 500)



MONGO_HOST = 'mongodb://localhost/test'

# Insert your keys here
CONSUMER_KEY = "tbR5tpW7Z1EVEkeDyFIPS3sMB"
CONSUMER_SECRET = "2ytnJoV4BiGfCUQ7JmqmtwTBJy7E8fIL1AYeC0apefiKi11dqq"
ACCESS_TOKEN = "1193461434-VHcyqQZKyntCLIjSLElD1ASvgeAYXIN351L7bTd"
ACCESS_TOKEN_SECRET = "WPdUYm40s3lKKSWuINeRDKbEd0HJa5cNsW4cTNudyMrs8"

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
auth_api = tweepy.API(auth)

# fetch data of the top 3 influencers
def fetch_userData(account_list):
    temp = []
    for account in account_list:
        item = auth_api.get_user(account)
        # description = item.description
        created_at = item.created_at
        followers = item.followers_count
        following = item.friends_count
        statuses_count = item.statuses_count
        location = item.location
        average_tweets = '%.2f'%(float(statuses_count) / float((datetime.datetime.utcnow() - created_at).days))
        temp.append([account, followers, following, statuses_count,average_tweets,location, created_at])
    df = pd.DataFrame(temp, columns= ['account','followers', 'following', 'statuses_count','average_tweets','location', 'created_at'])
    return df




# stream users' timeline
def stream_timeline(account):
    hashtags = []
    mentions =[]
    end_date = datetime.datetime.utcnow() - datetime.timedelta(days=365)
    tweet_number = 0
    texts =[]

    for status in Cursor(auth_api.user_timeline, id = account).items():
        tweet_number +=1
        if hasattr(status, 'entities'):
            entities = status.entities
            if 'hashtags' in entities:
                for content in entities['hashtags']:
                    if 'text' in content:
                        hashtag = content['text']
                        if hashtag is not None:
                            hashtags.append(hashtag)


            if 'user_mentions' in entities:
                for content in entities['user_mentions']:
                    if content is not None:
                        if 'screen_name' in content:
                            name = content['screen_name']
                            if name is not None:
                                mentions.append(name)

            texts.append(status.text)

            if status.created_at < end_date:
                break

    return hashtags, mentions, texts, tweet_number

if __name__ == "__main__":

    item = fetch_userData(
        ['BigHitEnt', 'gingerol95', 'btsvotingteam', 'modooborahae', 'BTSNewsBrasil', 'BTS_twt', 'unicefkorea',
         'ThrowbacksBTS', 'ARMYTEAMID'])
    print(item)