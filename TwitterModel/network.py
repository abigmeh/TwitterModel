# -*- coding: utf-8 -*-
from __future__ import division
from pymongo import MongoClient
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import font_manager as fm
from collections import Counter
import operator
import seaborn as sns
import utilities
import pandas as pd
import networkx as nx
import nltk
from operator import itemgetter
import community
import itertools
from numpy import savetxt
from numpy import genfromtxt
import  tweepy


CONSUMER_KEY = "tbR5tpW7Z1EVEkeDyFIPS3sMB"
CONSUMER_SECRET = "2ytnJoV4BiGfCUQ7JmqmtwTBJy7E8fIL1AYeC0apefiKi11dqq"
ACCESS_TOKEN = "1193461434-VHcyqQZKyntCLIjSLElD1ASvgeAYXIN351L7bTd"
ACCESS_TOKEN_SECRET = "WPdUYm40s3lKKSWuINeRDKbEd0HJa5cNsW4cTNudyMrs8"
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)



# Establish connection with database
client = MongoClient()
db = client.test
col = db.BTS

my_tweets = db.BTS.find()


#######################################################
# get the network between users
#######################################################

G = nx.Graph()

# create a list between retweet users and retweeted users
relation_list = []

for t in my_tweets:
    if t.get('retweet_id') is not None:
        relations = []

        relations.append(t['user_name'])
        relations.append(t['user_id'])
        relations.append(t['retweet_id']['user_name'])
        relations.append(t['retweet_id']['user_id'])
        relation_list.append(relations)

print(len(relation_list))
print(relation_list[1])
relation_list = set(map(tuple, relation_list))
relation_list = list(map(list, relation_list))

print(len(relation_list))
print(relation_list[:10])

# savetxt('relations.csv', relation_list, delimiter= ',', fmt='%s')


for pairs in relation_list:
    G.add_edge(pairs[1], pairs[3])

# At first, get the graph's information

print(nx.info(G))

print("Number of edges : {}".format(G.number_of_edges()))
print("Number of nodes : {}".format(G.number_of_nodes()))


# get the density
print(nx.density(G))

# Find the 20 most important nodes

# def centrality_nodes(measure):
#     degree_dict = dict(G.)


degree_dict = dict(G.degree(G.nodes()))
nx.set_node_attributes(G, degree_dict, 'degree')

sorted_degree = sorted(degree_dict.items(), key = itemgetter(1), reverse=True)

top100_nodes = []
users = []
for d in sorted_degree[:30]:
    top100_nodes.append(d)
    users.append(d[0])

print(top100_nodes)

G_100 = nx.Graph()
print(users)

for a in users:
    try:
        a_name = api.get_user(a)
        print(a)
        for b in users:
            b_name = api.get_user(b)
            status = api.show_friendship(source_id=a, target_id=b)
            if status[0].following == True:
                G_100.add_edge(a_name.screen_name, b_name.screen_name)
            if status[1].following == True:
                G_100.add_edge(b_name.screen_name, a_name.screen_name)

    except tweepy.error.TweepError:
        pass


print(nx.info(G_100))

pos = nx.spring_layout(G_100)

# pos = nx.circular_layout(G_100)
print(nx.density(G_100))

nx.DiGraph()
# nx.draw(G_100, pos, with_labels = True, edge_color = 'b', arrowsize=10)

nx.draw(G_100, pos, with_labels = True, edge_color = 'b', arrowsize=20, node_size=1200, node_color='lightblue',
    linewidths=0.25, font_size=7)
# nx.draw_networkx_labels(G_100,pos,font_size=7,font_family='sans-serif')
plt.figure(figsize=(40,40))
plt.show()


# pos = range(len(top10_nodes))
#
# values = [val[0] for val in top10_nodes]
#
# plt.barh(pos, values, align='center', color='yellowgreen')
#
# plt.yticks(pos, [val[0] for val in top10_nodes])
# plt.title('Top {} of {} captured'.format(10, type))
# plt.tight_layout()
# plt.show()


# savetxt('100_node.csv', top100_nodes, delimiter= ',',fmt='%s')

# top_100_node = genfromtxt('100_node.csv',delimiter=',')
# print(top_100_node)




# betweenness_dict = nx.betweenness_centrality(G)
# eigenvector_dict = nx.eigenvector_centrality(G)
#
# nx.set_node_attributes(G, betweenness_dict, 'betweenness')
# nx.set_node_attributes(G, eigenvector_dict, 'eigenvector')
#
# sorted_betweenness = sorted(betweenness_dict.items(), key = itemgetter(1), reverse= True)
# top20_betweenes = []
# for d in sorted_betweenness[:20]:
#     top20_betweenes.append(d)
#
# print("Top 20 nodes by betweenness :" , top20_betweenes)
#
#
# sorted_eigenvector = sorted(eigenvector_dict.items(), key=itemgetter(1), reverse=True)
# top20_eigenvector_ = []
# for d in sorted_eigenvector[:20]:
#     top20_eigenvector_.append(d)
#
# print("Top 20 nodes by eigenvector :" , sorted_eigenvector)
#
#
# communities = community.best_partition(G)
# nx.set_node_attributes(G, communities, 'modularity')
# class0 = [n for n in G.nodes() if G.nodes[n]['modulartity'] == 0]
# class0_eigenvector = {n:G.node[n]['eigenvector'] for n in class0}
#
# class0_sorted_eignvector = sorted(class0_eigenvector.items(), key = itemgetter(1), reverse= True)
#
# print("Modularity Class 0 sorted by Eigenvector Centrality:")
# for node in class0_sorted_eignvector[:5]:
#     print("Name: ", node[0], "| Eigenvector Centrality", node[1])
#
