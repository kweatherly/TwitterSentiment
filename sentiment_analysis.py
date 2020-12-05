import argparse
import os

# Google
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from oauth2client.client import GoogleCredentials

# Twitter
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import twitterconfig

def print_result(annotations):
    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude

    for index, sentence in enumerate(annotations.sentences):
        sentence_sentiment = sentence.sentiment.score
        print('Sentence {} has a sentiment score of {}'.format(
            index, sentence_sentiment))

    print('Overall Sentiment: score of {} with magnitude of {}'.format(
        score, magnitude))
    return 0

def analyze(content):
    client = language.LanguageServiceClient()

    document = types.Document(
        content=content,
        type=enums.Document.Type.PLAIN_TEXT)
    annotations = client.analyze_sentiment(document=document)

    print_result(annotations)

class TwitterStreamer():
    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        #This handles Twitter authetification and the connection to Twitter Streaming API
        l = StdOutListener(fetched_tweets_filename)
        auth = OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)
        stream = Stream(auth, l)

        #This line filter Twitter Streams to capture data by the keywords: 
        stream.filter(track=hash_tag_list)

class StdOutListener(StreamListener):
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        tweet = data.split(',"text":"')[1].split('","source')[0]
        if not tweet.startswith('RT'):
            print(tweet)
            analyze(tweet)
            #with open(fetched_tweets_filename,'a') as tf:
                #tf.write(result)
        return True

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google.json"

    print("Starting sentiment analyser")

    print("Authenticating with Google NLP service")
    credentials = GoogleCredentials.get_application_default()

    hash_tag_list = ['#OOTT', '#Crude', '#WTI']
    fetched_tweets_filename = "oilTweets.txt"

    print("Starting Twitter steamer")
    ts = TwitterStreamer()
    ts.stream_tweets(fetched_tweets_filename, hash_tag_list)
