from django.shortcuts import render,redirect
import tweepy
from textblob import TextBlob
import pandas as pd
import re
import matplotlib.pyplot as plt
import wikipedia
from . import analyse


def index(request):
    return render(request,"SAT/index.html")
def analysis_page(request):
    Tweet=request.POST.get("tweet")
    if '#' in Tweet:
        Tweet=Tweet.replace("#","")
    perc,positive_tweet,negative_tweet=sentiment_analysis(Tweet)
    text,img_url=wikipedia_summary(Tweet)
    condition,conclution=conclution_print(perc)
    return render(request,"SAT/tweet_page.html",{'tweet_name':Tweet,'tweet_summary':text,'image_url':img_url,'positive':perc[0],'neutral':perc[1],'negative':perc[2],'positive_tweet':positive_tweet,'negative_tweet':negative_tweet,"condition":condition,"conclution":conclution})


def sentiment_analysis(tweet):
    Tweet=tweet
    # Search word/hashtag value
    consumer_key = 'jg5EJyI91ByAA0G9HChF9zG1E'
    consumer_secret = '7KP7TZ3bgWLSZVwhxowP7HPoJozfZ724vA5xRlUpyeP033oXsE'
    access_token = '3198857976-KDkdPbJBD1EToFgiY0HjQuAIEGLpixEP1h1dl8M'
    access_token_secret = 't5aypqygCgUmU1b2ffbBqpjOOQo9J6yGMlgFtSxlwldZj'

    # Create the authentication object
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    posts = tweepy.Cursor(api.search_tweets, q=Tweet, lang="en").items(100)

    reslt = [tweet.text for tweet in posts]

    df = pd.DataFrame(data=reslt, columns=['Tweets'])

    # Cleaning the text
    df['Tweets'] = df['Tweets'].apply(cleanTxt)

    df['subjectivity'] = df['Tweets'].apply(getSubjectivity)
    df['Polarity'] = df['Tweets'].apply(getPolarity)

    df['Analysis'] = df['Polarity'].apply(getAnalysis)

    # get the percentage of positive tweets
    ptweets = df[df.Analysis == 'positive']
    ptweets = ptweets['Tweets']

    positive_percentage = round((ptweets.shape[0] / df.shape[0]) * 100, 1)

    # get the percentage of negative tweets
    ntweets = df[df.Analysis == 'Negative']
    ntweets = ntweets['Tweets']

    negative_percentage = round((ntweets.shape[0] / df.shape[0] * 100), 1)

    # get the percentage of neutral tweets
    ntweets = df[df.Analysis == 'Neutral']
    ntweets = ntweets['Tweets']

    neutral_percentage = round((ntweets.shape[0] / df.shape[0] * 100), 1)
    perc=[positive_percentage, neutral_percentage, negative_percentage]

    positive_tweet=print_positive_tweet(df)
    negative_tweet=print_negative_tweet(df)
    return perc,positive_tweet,negative_tweet







#Clean the text

#Create a function to clean the tweets
def cleanTxt(text):
  text=re.sub('@[A-Za-z0-9_]+','',text)#Removes mentions
  text=re.sub(r'#','',text)#Removing the '#' symbols
  text=re.sub(r'RT[\s]+','',text)#Removing RT
  text=re.sub(r"https\S+", "", text)#Remove the hyper link
  return text

#Create a function to get the subjectivity
def getSubjectivity(text):
  return TextBlob(text).sentiment.subjectivity

#Create  a function to get the polarity
def getPolarity(text):
    return analyse.sentiment_analyse(text)

    #return TextBlob(text).sentiment.polarity


#Create a function to compute the negative ,neutral and positive analysis
def getAnalysis(score):

    if score<0:
        return 'Negative'
    elif score==0:
        return 'Neutral'
    else:
        return 'positive'


def wikipedia_summary(tweet):
    try:
        result = wikipedia.summary(tweet, sentences=6)
        wp_page = wikipedia.page(tweet)

    except:
        result = "none"

    try:
        list_img_urls = wp_page.images
    except:
        list_img_urls = [""]
    if list_img_urls==[]:
        list_img_urls=[""]
    print(list_img_urls)

    return result,list_img_urls[0]


def print_positive_tweet(df):
    j = 1
    positive_tweet=[]
    sortedDF = df.sort_values(by=['Polarity'])
    for i in range(0, sortedDF.shape[0]):
        if (sortedDF['Analysis'][i] == 'positive'):
            positive_tweet.append(str(j) + ') ' + sortedDF['Tweets'][i])
            if j==5:
                break
            j = j + 1
    return positive_tweet

def print_negative_tweet(df):
    j = 1
    negative_tweet=[]
    sortedDF = df.sort_values(by=['Polarity'])
    for i in range(0, sortedDF.shape[0]):
        if (sortedDF['Analysis'][i] == 'Negative'):
            negative_tweet.append(str(j) + ') ' + sortedDF['Tweets'][i])
            if j==5:
                break
            j = j + 1
    return negative_tweet


def pie_chart(df):
    plt.clf()
    df['Analysis'].value_counts()
    plt.title('Sentiment Analysis')
    plt.xlabel('Sentiment')
    plt.ylabel('Counts')
    df['Analysis'].value_counts().plot(kind='pie')
    plt.savefig("SAT/static/SAT/tweet_page_styles/images/pies/img.png")

def bar_graph(df):
    plt.clf()
    df['Analysis'].value_counts()
    plt.title('Sentiment Analysis')
    plt.xlabel('Sentiment')
    plt.ylabel('Counts')
    df['Analysis'].value_counts().plot(kind='bar', color="#F2003C")
    plt.savefig("SAT/static/SAT/tweet_page_styles/images/bars/img.png")



def conclution_print(perc):
    positive_perc=perc[0]
    negative_perc=perc[2]
    neutral_perc=perc[1]
    cond=""
    conclution=""
    if 65<neutral_perc:
        cond="Neutral Tweet"
        conclution="The Tweet is a Neutral Tweet ....Since the percentage of the neutral tweets are higher when compared to Positive and Negative Tweets...."
    elif positive_perc>negative_perc and  (positive_perc/4)*3>negative_perc:
        cond="Positive Tweet"
        conclution="The Tweet is a Positive Tweet ....Since the percentage of the Positive tweets are higher when compared to Negative Tweets...."
    else:
        cond="Negative Tweet"
        conclution="The Tweet is a Negative Tweet ....Since the percentage of the Negative tweets are higher when compared to Postive Tweets...."

    return cond,conclution


