import requests
import requests
import operator

# Misc.
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax

import json
import pandas as pd
import tweepy
import re
from nltk.tokenize import word_tokenize
import unicodedata
import matplotlib.pyplot as plt
import numpy as np
import nltk
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
import string 
from colorama import Fore, Back, Style
import pandas as pd
import matplotlib.pyplot as plt
# from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# import pyLDAvis.sklearn
# from wordcloud import WordCloud
import nltk
nltk.download('punkt') 
import tweepy
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

sid = SentimentIntensityAnalyzer
BEARER_TOKEN="AAAAAAAAAAAAAAAAAAAAAB5YfgEAAAAA8%2FRTT3Nnwgza6pVWR%2BNmXmRJiVg%3D26OGddyuoGboEUQ25N9Z4yqE2fSiBmj9rQ0htAtHEIg1StjgdN"
client = tweepy.Client(bearer_token=BEARER_TOKEN)

def get_users(keywords):
    print("keywords in tweetpy:::::::",keywords)
    keyword_arr = [value.strip() for value in keywords.split(',')]
    search_query='"'+keyword_arr[0]+'"'
    for keyword in keyword_arr[1:10]:
        search_query=search_query+' OR "'+keyword+'"'
    search_query=search_query+" -is:retweet lang:en"
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",search_query)
    tweets_response=generate_tweets(search_query)
    tdf = pd.DataFrame(get_tweets_authors(tweets_response))
    tdf['text']= tdf['text'].apply(lambda x: x.lower())
    tdf['tweets_text'] = tdf['text'].replace(r'(@\w+|\"|\'|#\w+)','', regex=True) # Removal of Handlers(@) and Hashtags 
    tdf['tweets_text']=tdf['tweets_text'].replace(r'https\S+|www\S+https\S+','',regex=True) # Removal of URLs 
    tdf['tweets_text']=tdf['tweets_text'].replace(r'http\S+|www\S+https\S+','',regex=True) # Removal of URLs 
    tdf['filttered_tweets']=tdf['tweets_text'].replace(r'[^\w\s]','',regex=True) # Removal of all non alphanumeric characters
    tdf['final_tweets'] = tdf['filttered_tweets'].replace(r'[^\x00-\x7F]+', '', regex=True) # Remove non-English words
    tdf['final_tweets'] = tdf['final_tweets'].apply(remove_non_english) #Remove tweets which contains no non-english words
    tdf = tdf.drop_duplicates(subset='filttered_tweets', keep="first")  #Remove duplicates
    print("::::::::::::::::::::::::::::::::::::::::::")
    tdf['tokenized_tweets']=tdf['filttered_tweets'].apply(data_processing)
    tdf['stemm_tweets'] = tdf['tokenized_tweets'].apply(lambda x: stemming(x))
    tdf['vader_ana'] = tdf['stemm_tweets'].apply(polarity_score_vader)
    tdf['compound']  = tdf['vader_ana'].apply(lambda score_dict: score_dict['compound'])

    # tdf.loc[tdf['roberta_score'] == 'positive']
    tweet_dict={}
    for index, row in tdf.iterrows():
        tweet_dict[row['username']]=[row['text'],row['roberta_score']]
    # print(tweet_dict)
    return tweet_dict

def remove_non_english(text):
    return ''.join(c for c in text if unicodedata.category(c) == 'Lu' or unicodedata.category(c) == 'Ll')

def generate_tweets(search_query):
    tweets_response = []
    for response in  tweepy.Paginator(client.search_recent_tweets,
                        query = search_query,
                        user_fields = ['username', 'public_metrics', 'description', 'location'],
                        tweet_fields = ['created_at', 'geo', 'public_metrics', 'text'],
                        expansions = "author_id",
                        max_results = 100, limit = 100):
        tweets_response.append(response)
        return tweets_response

def get_tweets_authors(tweets_response):
    result = []
    authors = {}
    for response in tweets_response:
        for user in response.includes["users"]:
            authors[user.id] = {'username': user.username,
                                'followers': user.public_metrics["followers_count"],
                                'tweets': user.public_metrics["tweet_count"],
                                'description': user.description,
                                'location': user.location
                                }  
        for tweet in response.data:
            author_info = authors[tweet.author_id]
            result.append({
                            "author_id": tweet.author_id,
                            "username": author_info['username'],
                            "author_followers": author_info['followers'],
                            "author_tweets": author_info['tweets'],
                            "author_description": author_info['description'],
                            "author_location": author_info['location'],
                            "text": tweet.text,
                            "created_at": tweet.created_at,
                            "retweets": tweet.public_metrics['retweet_count'],
                            "replies": tweet.public_metrics['reply_count'],
                            "likes": tweet.public_metrics['like_count'],
                            "quote_count": tweet.public_metrics['quote_count']
                        })
    return result

def data_processing(text):
    token_tweets = word_tokenize(text)
    lPunct = list(string.punctuation)
    lStopwords = stopwords.words('english') + lPunct + ['rt', 'via', '...', '…', '"', "'", '`']
    filtered_text = [word for word in token_tweets if not word in lStopwords]
    return " ".join(filtered_text)

#converting tokenized data in root form
def stemming(data):
    tweetStemmer = nltk.stem.PorterStemmer()
    text = [tweetStemmer.stem(word) for word in data]
    return data

def polarity_score_vader(example):
    return sid.polarity_scores(example)  

def sentiment(label):
    if label <0:
        return "negative"
    elif label ==0:
        return "neutral"
    elif label>0:
        return "positive"