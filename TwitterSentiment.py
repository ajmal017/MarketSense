import tweepy #allows us to access Twitter's API
import pandas as pd #manipulate imported data
import numpy as np #run calculations
from textblob import TextBlob #word processer to parse through Tweets
import re #checks if a particular strings match
import dash #deploying analytical web app
import dash_core_components as dcc #extension for dash used for graph output
import dash_html_components as html #extension for dash used for html organizing
from dash.dependencies import Input, Output #used to allow input/output fields for search

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div(children=[

    html.Div(className="bodyclass", id='output-graph'),
   
    html.Div(children=[
        html.Div(children='Enter twitter keyword:'), 
        dcc.Input(id='input', value='TSLA', type='text'),
    ]),

])

@app.callback(
    Output(component_id='output-graph', component_property='children'),
        [Input(component_id='input', component_property='value')]
)


def mainFunc(input_data):

    CONSUMER_KEY = " "
    CONSUMER_SECRET = " "
    ACCESS_TOKEN = " "
    ACCESS_SECRET = " "

    def twitter_setup():

        try:
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET) 
            auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET) 
            api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
            return api

        except:
            print("Error: Authentication Failed")

    def clean_tweet(tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analize_sentiment(tweet):
        analysis = TextBlob(clean_tweet(tweet))
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    pullTweets = twitter_setup()
    tweets = pullTweets.search(q=[input_data], count=200)

    data = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
    data['SA'] = np.array([ analize_sentiment(tweet) for tweet in data['Tweets'] ])

    pos_tweets = [ tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] > 0]
    neu_tweets = [ tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] == 0]
    neg_tweets = [ tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] < 0]

    posSentiment = len(pos_tweets)*100/len(data['Tweets'])
    negSentiment = len(neg_tweets)*100/len(data['Tweets'])
    neuSentiment = 100*(len(data['Tweets']) - len(neg_tweets) - len(pos_tweets))/len(data['Tweets'])

    return dcc.Graph(
    id='pie-chart',
    figure={
            'data': [{
                'type': 'pie',
                'labels': ['Positive', 'Negative'],
                'values': [posSentiment, negSentiment]
            }],

            'layout':{
                'title':{
                    'text':"Twitter Sentiment for {}\n".format(input_data),
                },
            }
        }
    ),
    
if __name__ == '__main__':
    app.run_server(debug=True)

