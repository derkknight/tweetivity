from twython import Twython
from twython import TwythonStreamer
import pandas as pd
import twython
import numpy as np
from pandas import DataFrame, Series
import time
import json
import csv
from datetime import datetime

with open('config.json', 'r') as file:
    config = json.load(file)

CONSUMER_KEY = config['CONSUMER_KEY']
CONSUMER_SECRET = config['CONSUMER_SECRET']

twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET)

#followers = twitter.get_followers_ids(screen_name = "nisellaneous")["ids"]

def get_follower_statuses(follower_id, list):
    try:
        for status in twitter.get_user_timeline(user_id=follower_id, include_rts=True, count=200):
            tweet_id = status["id"]
            timestamp = datetime.strptime(status["created_at"].encode('utf-8')[4:16], '%b %d %H:%M')
            tweet = []
            tweet.extend(follower_id, tweet_id, timestamp)
            list.append(str(follower_id) + ',' + str(tweet_id) + ',' + timestamp)
        print list
    except twython.exceptions.TwythonAuthError:
        pass

def get_follower_statuses_canned():
    tweets = []
    with open('sample_tweets.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        firstLine = True
        for row in spamreader:
            if firstLine:
                firstLine = False
                continue
            row[2] = get_datetime_from_tweet(row[2])
            tweets.append(row)
    return tweets

def load_data(tweets):
    df = DataFrame(data=tweets, columns=['Follower ID', 'Tweet ID', 'Timestamp'])
    df.set_index(pd.DatetimeIndex(df['Timestamp']), inplace=True)
    return df

def get_datetime_from_tweet(string):
    return datetime.strptime(string[4:20] + string[26:], '%b %d %H:%M:%S %Y')

def get_tweets_by_day(df, day):
    print(df[df.index.weekday==day])
    return df[df.index.weekday==day]

def get_tweets_by_hour(df, hour):
    print(df[df.index.hour==hour])
    return df[df.index.hour==hour]


###Crunch stuff
def get_report(tweets):
    df = load_data(tweets)
    day = 0
    report_dict = {}
    while day < 6:
        day_frame = get_tweets_by_day(df, day)
        day_dict = {}
        hour = 0
        while hour < 24:
            day_dict[hour] = get_number_of_users(get_tweets_by_hour(day_frame, hour))
            hour += 1
        report_dict[day] = day_dict
        day += 1
    return report_dict


import json


def get_number_of_users(df):
    return df['Follower ID'].unique().size

def mainone():
    tweets = get_follower_statuses_canned()
    df = load_data(tweets)
    monday = get_tweets_by_day(df, 1)
    get_tweets_by_hour(monday, 1)


def main():
    tweets = get_follower_statuses_canned()
    report = get_report(tweets)
    report = json.dumps(report)
    print(report)

main()