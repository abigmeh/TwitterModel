import json
from collections import Counter
import wordcloud
from nltk.corpus import stopwords
import re
import operator
from matplotlib import font_manager as fm
from matplotlib import pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import tweepy
import csv

CONSUMER_KEY = "tbR5tpW7Z1EVEkeDyFIPS3sMB"
CONSUMER_SECRET = "2ytnJoV4BiGfCUQ7JmqmtwTBJy7E8fIL1AYeC0apefiKi11dqq"
ACCESS_TOKEN = "1193461434-VHcyqQZKyntCLIjSLElD1ASvgeAYXIN351L7bTd"
ACCESS_TOKEN_SECRET = "WPdUYm40s3lKKSWuINeRDKbEd0HJa5cNsW4cTNudyMrs8"


def clean(text):
    #     Stopwords = set(stopwords.words('english'))
    #     words = word_tokenize(text)
    #     word_filter = []
    #
    #     for w in words:
    #         if w not in Stopwords:
    #             word_filter.append(w)
    #     re_text = re.findall("RT @[\w]*:", text)
    patten1 = r"RT @[\w]*:"
    patten2 = r"@[\w]*"
    patten3 = r"\n"
    patten4 = r"https?://[A-Za-z0-9./]*"
    patten5 = r'#[\w]*'
    combined_pat = r'|'.join((patten1, patten2, patten3, patten4, patten5))
    re_text = re.sub(combined_pat, ' ', text)

    return re_text


# store all  hashtags
def get_hashtags(tweets):

    hashtag_list = []

    for t in tweets:
        if 'hashtags' in t:
            hashtag_list.append(t['hashtags'])

    return hashtag_list


def filter_eng_text(tweets):
    eng_tweets = []
    for t in tweets:
        if t["language"] =='en':
            eng_tweets.append(t['text'])
    return eng_tweets


def analyze_sentiment(tweet_text,analyzer):
    filter_scores = []
    pos_text = []
    neg_text = []
    neu_text = []
    for single_tweet in tweet_text:
        score = analyzer.polarity_scores(single_tweet)
        compound_score = score['compound']
        if compound_score >= 0.05:
            filter_scores.append(1)
            pos_text.append(single_tweet)
        elif compound_score <= -0.05:
            filter_scores.append(-1)
            neg_text.append(single_tweet)
        else:
            filter_scores.append(0)
            neu_text.append(single_tweet)

    return filter_scores,pos_text,neu_text,neu_text


# this only used to analyze the topic of some fan account
# in order to see if they talk about another things except bts
# def remove_emos(tweets)


## get the influencers among the fans
def get_influencer(tweets):
    retweet_users = []
    for t in tweets:
        if 'retweet_id' in t:
            l = t.get('retweet_id','')
            retweet_users.append(l.get('user_id'))
    return retweet_users

##################################################################
# get the most retweeted tweets
##################################################################

def get_most_retweets(tweets, n):
    retweet_id_list = []
    retweets = []
    for t in tweets:
        if'retweet_id' in t:
            l = t.get('retweet_id', '')
            retweet_id_list.append(l.get('tweet_id'))
            retweets.append(l.get('text'))
    rtl = Counter(retweet_id_list)
    topn = dict(rtl.most_common(n))

    return topn


def plot_horizonBar_text(list, number, type):
    r = Counter(list)
    subset = dict(r.most_common(number))
    sorted_subset = sorted(subset.items(), key=operator.itemgetter(1))
    prop = fm.FontProperties(fname='SourceHanSans.ttc')

    pos = range(len(sorted_subset))

    values = [val[1] for val in sorted_subset]
    max_value = max(values)
    min_value = min(values)
    plt.barh(pos, values, align='center', color='yellowgreen')
    for i, v in enumerate(values):
        if v < max_value/2:
            plt.text(min_value+v, i-0.15, str(v) , ha = 'center',color='black')
        else:
            plt.text(v-min_value, i-0.15, str(v), ha = 'center', color = 'white')

    plt.yticks(pos, [val[0] for val in sorted_subset],fontproperties=prop)
    plt.title(' {} most common {} '.format(number, type))
    plt.tight_layout()
    plt.show()



def plot_horizonBar_normal(list, number, type):
    r = Counter(list)
    subset = dict(r.most_common(number))
    sorted_subset = sorted(subset.items(), key=operator.itemgetter(1))

    pos = range(len(sorted_subset))

    values = [val[1] for val in sorted_subset]

    plt.barh(pos, values, align='center', color='yellowgreen')

    plt.yticks(pos, [val[0] for val in sorted_subset])
    plt.title('Top {} of {} captured'.format(number, type))
    plt.tight_layout()
    plt.show()



# get the first 500 tweets from the top 3 influencers

def get_wordcloud(tweet_text, type):
    all_words = ''.join(word for word in tweet_text)
    stopwords = set(STOPWORDS)
    wordcloud = WordCloud(stopwords=stopwords, colormap='jet', max_words=50, max_font_size=200,
                          background_color="white").generate(all_words)

    # plt.figure(figsize=(12,0))
    plt.imshow(wordcloud,interpolation='bilinear')
    plt.title('Word Cloud of {}'.format(type))
    plt.axis('off')
    plt.show()

## analyze what equipment the fans usually use to tweet
def get_source(tweets):
    source_list = []
    for t in tweets:
        source_list.append(t['source'])
    return source_list


