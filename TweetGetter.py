from twython import Twython
from twython import TwythonStreamer
from pandas import DataFrame, Series
from datetime import datetime, date, time, timedelta
import pandas as pd
import numpy as np
import twython
import time
import csv
import json

class TooManyFollowersException(Exception):
    pass

timezone = 0

# Initialize 
with open('config.json', 'r') as file:
    config = json.load(file)
CONSUMER_KEY = config['CONSUMER_KEY']
CONSUMER_SECRET = config['CONSUMER_SECRET']
twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET)

def set_timezone(utcoffset):
    timezone = utcoffset

# Returns a list of user_ids of followers
def get_followers_of_user(screen_name):
    followers = twitter.get_followers_ids(screen_name = screen_name)["ids"]
    if (len(followers) > 400):
        return -1
    return followers

# Given a list of raw tweets, load in the data and return a pandas DataFrame
def load_data(tweets):
    df = DataFrame(data=tweets, columns=['Follower ID', 'Tweet ID', 'Timestamp'])
    df.set_index(pd.DatetimeIndex(df['Timestamp']), inplace=True)
    df = df.tz_localize((timezone*10*6)*-1, level=0)
    return df

# 
# Exception is used in the case of private account.
def get_follower_statuses(follower_id, list):
    try:
        for status in twitter.get_user_timeline(user_id=follower_id, include_rts=True, count=200):
            tweet_id = status["id"]
            timestamp = status["created_at"].encode('utf-8')
            tweet = []
            tweet.append(str(follower_id))
            tweet.append(str(tweet_id))
            tweet.append(get_datetime_from_tweet(timestamp))
            list.append(tweet)
    except twython.exceptions.TwythonAuthError:
        pass

def average_day(df):
    day = int(datetime.today().strftime("%w"))
    day_frame = get_tweets_by_day(df, day).groupby(pd.Grouper(freq='1H')).nunique()
    day_frame = day_frame[(day_frame.T != 0).any()]
    return day_frame
    
def get_tweets_by_week(df, week):
    lol = datetime.today() - timedelta(weeks = week)
    return df[(df.index > lol.strftime("%Y-%m-%d")) & (df.index <= datetime.today().strftime("%Y-%m-%d"))]

# Helper function to convert string to datetime
def get_datetime_from_tweet(string):
    return datetime.strptime(string[4:20] + string[26:], '%b %d %H:%M:%S %Y')

# Using the DataFrame and given a day (0=Mon, 6=Sun), find all entries in that day
def get_tweets_by_day(df, day):
    return df[df.index.weekday==day]

# Using the DataFrame and given an hour, find all entries in that hour
def get_tweets_by_hour(df, hour):
    return df[df.index.hour==hour]


def get_report(screen_name):
    followers = get_followers_of_user(screen_name)
    if (followers == -1):
        raise TooManyFollowersException("High volume of followers. Can't compute.")
    tweets = []
    for follower in followers:
        get_follower_statuses(follower, tweets)
    df = load_data(tweets)
    df = get_tweets_by_week(df, 3)
    df = average_day(df)
    report_dict = []
    hour = 0;
    while hour < 24:
        #get the mean of each hour
        meanFloat = get_tweets_by_hour(df, hour)["Follower ID"].mean()
        mean = 0
        if (np.isnan(meanFloat) == False):
            mean = int(np.ceil(meanFloat))
        report_dict.append(mean)
        hour += 1
    return report_dict
    

# Gets the count of unique users.
def get_number_of_users(df):
    return df['Follower ID'].unique().size

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