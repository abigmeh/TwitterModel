# -*- coding: utf-8 -*-
import operator
from pymongo import MongoClient
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import font_manager as fm
import matplotlib.cm as cm
from collections import Counter
import utilities
import pandas as pd
import numpy as np
from mpl_toolkits.basemap import Basemap

# Set ipython's max row display
pd.set_option('display.max_row', 1000)

# Set iPython's max column width to 50
pd.set_option('display.max_columns', 50)

# Establish connection with database
client = MongoClient()
db = client.test
col = db.BTS

my_tweets = db.BTS.find()

df = pd.DataFrame()

#######################################################
# get location
#######################################################
userid_list = []
tweetid_list = []
location_list = []
source_list = []
hashtags = []


# get tweet, userid, username, location, text, source, language, hashtags
for t in my_tweets:
    if t.get('location') is not None:
        userid_list.append(t['user_id'])
        tweetid_list.append(t['tweet_id'])
        location_list.append(t['location'])
        source_list.append(t['source'])

        if t.get('hashtags') is not None:
            hashtags.append(t['hashtags'])
        else:
            hashtags.append(('null'))
df.insert(0,'user_id', userid_list)
df.insert(1,'tweet_id', tweetid_list)
df.insert(2,'location', location_list)
df.insert(3,'source',source_list)
df.insert(4,'hashtags',hashtags)


df.to_csv('location.csv')

location_df = pd.read_csv('location.csv')
location_df.drop(location_df.columns[[0]], axis= 1,inplace=True)

filter_users = np.unique(location_df.user_id)

print("Among fetched tweets, there are",len(location_df), "tweets contain location information "
      "which are published by",len(filter_users), "users")

# location_df.sort_values('user_id', inplace= True)
drop_duplicates_df = location_df.drop_duplicates(subset=['user_id'])

utilities.plot_horizonBar_text(location_df['location'], 15, 'locations')

utilities.plot_horizonBar_text(drop_duplicates_df['location'], 15, 'locations from unique users')

# get most 15 common countries
def location_relation(dataframe, common_number):
    r = Counter(dataframe['location'])
    subset = dict(r.most_common(common_number))
    print(subset)
    sorted_subset = sorted(subset.items(), key=operator.itemgetter(1), reverse=True)
    countries = []
    for i in range(len(sorted_subset)):
        country = np.array(sorted_subset)[i][0]
        countries.append(country)
    most_common_df= dataframe[dataframe.location.isin(countries)]
    most_common_df.to_csv('most_common_location.csv')

location_relation(drop_duplicates_df,15)

most_location_df = pd.read_csv('most_common_location.csv')

def combine_location(dataframe, which_country, to_country):
    dataframe.loc[dataframe['location'] == which_country, 'location'] = to_country
    return dataframe

combine_location(most_location_df, '대한민국', 'Korea')
combine_location(most_location_df, 'ประเทศไทย', 'Thailand')
combine_location(most_location_df, 'Việt Nam', 'Vietnam')
combine_location(most_location_df, 'Seoul, Republic of Korea', 'Korea')
combine_location(most_location_df, 'Republic of the Philippines', 'Philippines')
combine_location(most_location_df, '대한민국 서울', 'Korea')
combine_location(most_location_df, 'กรุงเทพมหานคร, ประเทศไทย', 'Thailand')
combine_location(most_location_df, '🇵🇭', 'Philippines')
combine_location(most_location_df, '日本', 'Japan')


most_location_df.to_csv("combine_location.csv")

utilities.plot_horizonBar_text(most_location_df['location'], 10, 'locations - Combined')
print(most_location_df.loc[:10])

most_common_source = ['Twitter for Android', 'Twitter for iPhone','Twitter Web App','Twitter for iPad']
most_location_df.loc[~most_location_df['source'].isin(most_common_source),'source' ] = 'other'
utilities.plot_horizonBar_normal(most_location_df['source'], 5,'source')
most_location_df.groupby(['location','source']).size().unstack().plot(kind='bar',stacked=True)
plt.ylim(0, 5500)
plt.ylabel('Source number')
plt.show()


def get_most_common(list, number):
    r = Counter(list)
    subset = dict(r.most_common(number))
    return subset

def get_country_hashtag(dataframe, country,number):
    filtered_df = dataframe[dataframe[['location', 'hashtags']].notnull().all(1)]
    # filtered_df['hashtags'] = filtered_df['hashtags'].astype(str).str.lstrip('[').str.rstrip(']')
    hashtag_list = filtered_df.loc[filtered_df['location'] == country,'hashtags']

    hash_list = get_most_common(hashtag_list,number)
    return hash_list.keys()

coutries = np.array(most_location_df['location'].unique())


for country in coutries:
    country_dict = dict()
    country_name = 'coutry_{}'.format(country)
    country_hash = get_country_hashtag(most_location_df, country,1)
    country_dict[country] = country_hash
    print(country_dict)



m = Basemap(projection= 'mill', llcrnrlat=-60, urcrnrlat= 90, llcrnrlon= -180, urcrnrlon= 180, resolution='c')
m.drawcoastlines()
m.drawcountries()
m.drawparallels(np.arange(-90,90,30), labels= [True, False, False, False])
m.drawmeridians(np.arange(-180, 180, 60), labels= [0,0,0,1])
bbox_props = dict(fc='white', ec='green', lw=1, boxstyle='round,pad=0.1')

# countries = [Korea, Indonesia, United States, México, Japan, Philippines, Brasil, Thailand, Malaysia ,Vietnam]
lat_y = [35.9078, 0.7893, 37.0902 , 23.6345 , 36.2048 , 12.8797,-14.2350 ,15.8700,4.2105, 14.0583]
lon_x = [127.7669,113.9213, -95.7129 , -102.5528 ,138.2529, 121.7740 , -51.9253,100.9925,101.9758 ,108.2772]

colors = cm.rainbow(np.linspace(0, 1, 10))

m.scatter(lon_x, lat_y, latlon= True, s =150, c=colors, marker = '.', edgecolor='k', zorder=2)



plt.annotate('$\\bf{Korea}$\n $\it{BTS}$', m(127.7669,35.9078), xytext=m(110,80), fontsize=10,
             fontname='Arial', color='red', ha='center', va='center',
            arrowprops=dict(color='red', arrowstyle="->"),
            bbox= bbox_props)

plt.annotate('$\\bf{Indonesia}$\n $\it{BTS}$', m(113.9213,0.7893), xytext=m(140,-30), fontsize=10,
             fontname='Arial', color='red', ha='center', va='center',
            arrowprops=dict(color='red', arrowstyle="->"),
            bbox= bbox_props)

plt.annotate('$\\bf{United States}$\n $\it{BTS}$', m(-95.7129,37.0902), xytext=m(-150,60), fontsize=10,
             fontname='Arial', color='red', ha='center', va='center',
            arrowprops=dict(color='red', arrowstyle="->"),
            bbox= bbox_props)

plt.annotate('$\\bf{México}$\n $\it{BTS,MAMAVOTE}$', m(-102.5528,23.6345), xytext=m(-150,-30), fontsize=10,
             fontname='Arial', color='red', ha='center', va='center',
            arrowprops=dict(color='red', arrowstyle="->"),
            bbox= bbox_props)

plt.annotate('$\\bf{Japan}$\n $\it{BTS,MAMAVOTE}$', m(138.2529,36.2048), xytext=m(160,60), fontsize=10,
             fontname='Arial', color='red', ha='center', va='center',
            arrowprops=dict(color='red', arrowstyle="->"),
            bbox= bbox_props)

plt.annotate('$\\bf{Philippines}$\n $\it{BTS,MAMAVOTE}$', m(121.7740,12.8797), xytext=m(190,10), fontsize=10,
             fontname='Arial', color='red', ha='center', va='center',
            arrowprops=dict(color='red', arrowstyle="->"),
            bbox= bbox_props)


plt.annotate('$\\bf{Brasil}$\n $\it{BTS,MAMAVOTE}$', m(-51.9253,-14.2350), xytext=m(-30,30), fontsize=10,
             fontname='Arial', color='red', ha='center', va='center',
            arrowprops=dict(color='red', arrowstyle="->"),
            bbox= bbox_props)


plt.annotate('$\\bf{Thailand}$\n $\it{BTS}$', m(100.9925,15.8700), xytext=m(40,-30), fontsize=10,
             fontname='Arial', color='red', ha='center', va='center',
            arrowprops=dict(color='red', arrowstyle="->"),
            bbox= bbox_props)

plt.annotate('$\\bf{Malaysia}$\n $\it{BTS}$', m(101.9758,4.2105), xytext=m(100,-60), fontsize=10,
             fontname='Arial', color='red', ha='center', va='center',
            arrowprops=dict(color='red', arrowstyle="->"),
            bbox= bbox_props)

plt.annotate('$\\bf{Vietnam}$\n $\it{BTS,MakeItRight}$', m(108.2772,14.0583), xytext=m(60,60), fontsize=10,
             fontname='Arial', color='red', ha='center', va='center',
            arrowprops=dict(color='red', arrowstyle="->"),
            bbox= bbox_props)

fig = plt.figure()
fig.set_tight_layout(True)

plt.show()