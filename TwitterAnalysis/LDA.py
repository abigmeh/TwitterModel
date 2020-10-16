from gensim import corpora, models
import utilities
import re, string
from nltk.corpus import stopwords
import nltk
from pymongo import MongoClient
import numpy as np
from nltk.stem import WordNetLemmatizer
import gensim
import pyLDAvis.gensim
import pickle
import influencerAnalyze
from imp import reload


client = MongoClient()
db = client.test
my_tweets = db.brexit.find()
numTweets = db.brexit.estimated_document_count()




# clean text into only English text, no emojis, no emocons,no stopwords, no punctuations

def remove_emojis(text):
    output = ""
    for character in text:
        try:
            character.encode("ascii")
            output += character
        except UnicodeEncodeError:
            output += ''
    return output


english_stopwords = stopwords.words('english')
english_stopwords.extend(['from', 'subject', 're', 'edu', 'use'])
punctuations= string.punctuation
punctuations_extra = [ '...','..','``',"''"] # adding more examples of punctiations
remove_info = set(english_stopwords).union(set(punctuations)).union(set(punctuations_extra))
lemmatizer = WordNetLemmatizer()

# def get_gram(texts):
#     data_words =[]
#     for line in texts:
#         text = utilities.clean(line)
#         text = remove_emojis(text)
#         text = [word for word in nltk.word_tokenize(text.lower())]
#         data_words.append(text)
#
#     bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100)
#     trigram = gensim.models.Phrases(bigram[data_words], threshold=100)
#
#     bigram_mod = gensim.models.phrases.Phrases(bigram)
#     trigram_mod = gensim.models.phrases.Phrases(trigram)
#     return bigram, bigram_mod, trigram, trigram_mod

def filter_tweet(tweet_text):
    filtered_tweet = []
    for line in tweet_text:
        text = utilities.clean(line)
        text = remove_emojis(text)
        text = [word for word in nltk.word_tokenize(text.lower())]
        text = [lemmatizer.lemmatize(word, pos = 'v') for word in text]
        text = [word for word in text if word not in remove_info and len(word)>2]
        if text:
            filtered_tweet.append(text)
    return filtered_tweet

tweets = utilities.filter_eng_text(my_tweets)
filtered_tweet = filter_tweet(tweets)



accounts = ['modooborahae','gingerol95','btsvotingteam']

if __name__ == "__main__":
# for account in accounts:
#     hashtags, mentions, texts, tweet_number = influencerAnalyze.stream_timeline(account)
#     filtered_tweet = filter_tweet(texts)

    # build the dicionary
    dictionary = gensim.corpora.Dictionary(filtered_tweet)
    count = 0
    for k, v in dictionary.items():
        count +=1
        if count > 10:
            break
    bow_corpus = [dictionary.doc2bow(doc) for doc in filtered_tweet]

    # pickle.dump(bow_corpus, open('bow_corpus.pkl', 'wb'))
    # dictionary.save('dictionary.gensim')

    # take the 101 document as a sample
    # bow_sample = bow_corpus[100]
    # for i in range(len(bow_sample)):
    #     print("Word {} (\"{}\") appears {} time.".format(bow_sample[i][0], dictionary[bow_sample[i][0]],
    #                                                       bow_sample[i][1]))

    tfidf = models.TfidfModel(bow_corpus)
    corpus_tfidf = tfidf[bow_corpus]
    # lda_model =models.LdaMulticore(bow_corpus, num_topics=10,id2word=dictionary, passes=2, workers=2)
    # for idx, topic in lda_model.print_topic():
    #     print('User {} has topic: {} \nWords: {}'.format(account, idx, topic))
    # for idx, topic in lda_model.show_topics(formatted=False, num_words= 10):
    #     print('Topic: {} \nWords: {}'.format(idx, '|'.join([w[0] for w in topic])))
    #

    # lda_model = models.LdaModel(bow_corpus, num_topics=10, id2word=dictionary, passes=15)
    # lda_model.save('ldamodel.gensim')


    # topics = lda_model.print_topics(num_topics=4)
    # for topic in topics:
    #     print(topic)
    #

    lda_model = gensim.models.ldamodel.LdaModel(corpus=bow_corpus, id2word=dictionary, num_topics=7, random_state=100,
                                                update_every=1, chunksize=100, passes=10, alpha='auto', per_word_topics=True)

    print(lda_model.print_topics())

    print('\nPerplexity: ', lda_model.log_perplexity(bow_corpus))

    coherence_model_lda = gensim.models.CoherenceModel(model=lda_model, texts=filtered_tweet,dictionary= dictionary,
                                                       coherence='c_v')
    coherence_lda = coherence_model_lda.get_coherence()

    print('\nCoherence Score: ', coherence_lda)

    vis = pyLDAvis.gensim.prepare(topic_model=lda_model, corpus=bow_corpus, dictionary=dictionary)
    # pyLDAvis.save_html(vis, '{}_LDA_Visualization.html'.format(account))
    pyLDAvis.save_html(vis, 'brexit_LDA_Visualization.html')
