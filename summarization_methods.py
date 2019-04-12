import pandas as pd
from collections import Counter
import numpy as np
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.decomposition import LatentDirichletAllocation as LDA
from nltk.stem import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
import torch
from allennlp.commands.elmo import ElmoEmbedder
import scipy
import random
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
warnings.filterwarnings("ignore")
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
from bs4 import BeautifulSoup
import string, unicodedata
import re
from nltk.corpus import wordnet
import os
from langdetect import detect
from sklearn.feature_extraction.text import CountVectorizer

def KL_sum(orig, doc, num_sents):
    def KL(sen_words, doc_count):
        length_sen = len(sen_words)
        length_doc = sum(doc_count.values())
        sen_count = Counter(sen_words)

        kl_score = 0
        for item in sen_count.keys():
            p = doc_count[item]/length_doc
            q = sen_count[item]/length_sen
            kl_score += p * np.log(p / q)
        return kl_score
    
    doc_words = [word for line in doc for word in line.split(" ")]
    doc_count = Counter(doc_words)
    sentences = [line.split(" ") for line in doc]
    sen_score = [KL(sent,doc_count) for sent in sentences]
    
    pos = []
    num_output = 0
    l = 0
    pos = np.argsort(sen_score)[:num_sents]
    summ = [orig[i] for i in pos]
    
    return " ".join(summ)


def query_sum(raw_sents, new_sents, querys, num_sents):
    vectors = []
    for i in range(len(new_sents)):
        vec = elmo.embed_sentence(new_sents[i].split())
        vectors.append(np.mean(vec, axis = 1).reshape(1,-1)[0])
    
    query_dict = {}
    for que in querys:
        #print(que)
        query = np.mean(elmo.embed_sentence(que.split()), axis = 1).reshape(1,-1)[0]
        similarities = cosine_similarity([query], vectors)
        # Sample from top 5% to avoid redundance. 
        pos = np.argsort(similarities)[0][::-1][:num_sents]
        #pos = np.random.choice(pos, num_sents, replace=False)
        query_dict[que] = list(np.array(raw_sents)[pos])
    return query_dict


elmo = ElmoEmbedder()
# Embedding + Cluster + Sample
def cluster_sum(raw_sents, new_sents, n_clusters):
    vectors = []
    for i in range(len(new_sents)):
        vec = elmo.embed_sentence(new_sents[i].split())
        vectors.append(np.mean(vec, axis = 1).reshape(1,-1)[0])
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(vectors)
    distances = kmeans.transform(vectors)
    pos = np.argmin(distances, axis = 0)
    return np.array(raw_sents)[pos]