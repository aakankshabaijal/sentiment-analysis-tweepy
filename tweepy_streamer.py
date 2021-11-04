from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor

import numpy as np
import pandas as pd
import twitter_credentials

'''
DOCS for Tweepy API : https://docs.tweepy.org/en/stable/api.html#tweets
'''

#### TWITTER CLIENT ####
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user


    def getTwitterClientAPI(self):
        return self.twitter_client

    def getUserTimelineTweets(self, numTweets):
        '''
        Returns a list of tweets from the user's timeline (ones that the user posted or retweeted)
        '''
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(numTweets):
            tweets.append(tweet)
        return tweets 

    def getFriendList(self, numFriends):
        '''
        Returns a list of length numFriends containing the user's friends in order of most recent
        '''
        friendList = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(numFriends):
            friendList.append(friend)
        return friendList

    def getHomeTimelineTweets(self, numTweets):
        '''
        Returns a list of length numTweets containing tweets from home feed
        '''
        homeTweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(numTweets):
            homeTweets.append(tweet)
        return homeTweets
       

#### TWITTER AUTHENTICATOR ####
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth

#### TWITTER STREAMER ####
class TwitterStreamer():
    '''
    A class for streaming and processing live tweets.
    '''
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def  stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authetication and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener) #streaming tweets

        #This line filter Twitter Streams to capture data by the keywords in the hash tag list
        stream.filter(track=hash_tag_list)


#### TWITTER LISTENER ####
class TwitterListener(StreamListener):
    '''
    This is a basic listener that appends the tweets to a file.
    '''
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf: #appending to file
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
            return True

    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case we exceed rate limit of twitter
            return False
        print(status) 


class TweetAnalyzer():
    '''
    Functionality for analyzing and categorizing content from tweets.
    '''
    def tweetsToDataFrame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets']) #extracting text from tweets
        return df

if __name__ == '__main__':
    # hash_tag_list = ['apple', 'google', 'samsung']
    # fetched_tweets_filename = "tweets.json"    
    # twitter_client = TwitterClient('elonmusk') #any particular user whose tweets you want to fetch
    # print(twitter_client.getUserTimelineTweets(5))
    # twitterStreamer = TwitterStreamer()
    # twitterStreamer.stream_tweets(fetched_tweets_filename, hash_tag_list)

    twitter_client = TwitterClient('elonmusk')
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.getTwitterClientAPI()

    tweets = api.user_timeline(screen_name="elonmusk", count=20)
    df = tweet_analyzer.tweetsToDataFrame(tweets)
    print(df.head(10))
    