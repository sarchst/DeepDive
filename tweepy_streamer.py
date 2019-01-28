from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import twitter_credentials

class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id = self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id = self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Curor(self.twitter_client.home_timeline, id = self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


class TwitterAuthenticator():

    def authenticate_twitter_app(self):
            auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
            auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
            return auth

class TwitterStreamer():
    """
    Class for streaming and processing life tweets
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename,hash_tag_list):
        # This handles Twitter authentication and connection to the TwitterStreamer
        # streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        stream.filter(track=hash_tag_list)


class TwitterListener(StreamListener):
    """
    This is a basic listener class that just prints recieved tweets to stdout
    """
    def __init__ (self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data): #take in data from streamlistener and do something with it
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                    tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status):# gets called if there is an on_error
        if status == 420:
            #returning false on data method incase rate limmit occurs
            return False
        print(status)

class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing ocntent from tweets
    """
    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data = [tweet.text for tweet in tweets], columns = ['Tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df



if __name__ == "__main__":
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()
    tweets = api.user_timeline(screen_name="realDonaldTrump", count=200)
    #print(dir(tweets[0])) # all the things we can possibly ask for
    #print(tweets[0].retweet_count)
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    #print(df.head(10))
    #avergae length of all the 20 tweets
    print(np.mean(df['len']))
    # get the number of likes for the most liked tweets
    print(np.max(df['likes']))

    print(np.max(df['retweets']))

    # Time Series
    time_retweets = pd.Series(data=df['retweets'].values, index = df['date'])
    time_retweets.plot(figsize=(16,4), label='retweets', legend=True)

    time_likes = pd.Series(data=df['likes'].values, index = df['date'])
    time_likes .plot(figsize=(16,4), label='likes', legend=True)

    plt.show()
