import json
from NewsHandler import NewsHandler
from ElasticSearchServices import ElasticSearchServices
import random,operator
import ConfigParser
#----------------------------------
# For sending News Requests
import requests

f = open("API_KEY.txt")
api_key = f.read()
config = ConfigParser.ConfigParser()
config.readfp(open(r'./configurations.txt'))
#----------------------------------
# Sentiment Analysis
import re
import sys
from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 as features
#----------------------------------

#---- Elastic Search Details -------

index = "news2"
collection = {
	"mappings": {
		"article": {
			"properties": {
				"title": {
					"type": "string"
				},
				"author": {
					"type": "string"
				},
                "url": {
                    "type": "string"
                },
                "url2image": {
                    "type": "string"
                },
				"source": {
					"type": "string"
				},
                "timestamp": {
                    "type": "string"
                },
				"location": {
					"type": "geo_point"
				},
                "sentiment": {
                    "type": "string"
                },
                "dominant_emotion": {
                    "type": "string"
                },
                "anger": {
                    "type": "float"
                },
                "joy": {
                    "type": "float"
                },
                "sadness": {
                    "type": "float"
                },
                "fear": {
                    "type": "float"
                },
                "disgust": {
                    "type": "float"
                }
			}
		}
	}
}


#--------------------------------------------------------


try:
    collection_service = ElasticSearchServices()
    collection_service.create_collection(index, collection)
except:
    print "Index already created"

def clean(text):
    '''
    Utility function to clean text by removing links, special characters
    using simple regex statements.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())

def sentimentAnalysis(text):
    Username = config.get('Watson Credentials', 'Username')
    Password = config.get('Watson Credentials', 'Password')

    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2017-02-27',
        username=Username,
        password=Password)


    response = natural_language_understanding.analyze(
        text=text,
        features=[features.Emotion(), features.Sentiment()])

    emotion_dict = response['emotion']['document']['emotion']
    overall_sentiment = response['sentiment']['document']['label']

    return overall_sentiment, emotion_dict

def fetchArticles():
    news_handler = NewsHandler()

    source_requests = requests.get('https://newsapi.org/v1/sources?language=en')

    source_json_data = source_requests.json()
    base_url = 'https://newsapi.org/v1/articles?source='

    for i in source_json_data['sources']:
        source = str(i['name'])
        print source
        print '--------'
        url = base_url + i['id']
        url = url + '&sortBy='
        for j in i['sortBysAvailable']:
            url_final = url + j + '&apiKey=' + api_key
            r = requests.get(url_final)
            for k in r.json()['articles']:
                print k['title']
                print k['author']
                print k['url']
                print k['urlToImage']
                print k['publishedAt']
                title = str(k['title'])
                author = str(k['author'])
                url = str(k['url'])
                url2image = str(k['urlToImage'])
                timestamp =  str(k['publishedAt'])
                # Generating random geolocation data
                final_longitude=random.uniform(-180.0,180.0)
                final_latitude=random.uniform(-90.0, +90.0)
                location_data = [final_longitude, final_latitude]

                cleaned_title = clean(title)

                # Sentiment analysis on title
                sentiment, allemotions = sentimentAnalysis(cleaned_title)
                anger=allemotions['anger']
                joy=allemotions['joy']
                sadness=allemotions['sadness']
                fear=allemotions['fear']
                disgust=allemotions['disgust']
                dominant_emotion = find_dominant_emotion(anger, joy, sadness, fear, disgust)

                # Inserting News Article to Storage
                print(news_handler.insertNews(title, author, url, url2image, source, timestamp, location_data, sentiment, dominant_emotion, anger, joy, sadness, fear, disgust))

def find_dominant_emotion(anger, joy, sadness, fear, disgust):
    emo_dictionary = {}
    emo_dictionary["anger"] = anger
    emo_dictionary["joy"] = joy
    emo_dictionary["sadness"] = sadness
    emo_dictionary["fear"] = fear
    emo_dictionary["disgust"] = disgust

    return max(emo_dictionary.iteritems(), key=operator.itemgetter(1))[0]

def startFetch():
        try:
            print 'Fetching News Articles!'
            fetchArticles()
        except Exception, e:
            print("Exception in fetching News Articles:" + str(e))
