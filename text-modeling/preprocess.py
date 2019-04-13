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
import os
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

# Sentences Filter
def sent_filter(sent):
    def name_entity(sent):
        """Identify names in a sentence"""
        nlp = en_core_web_sm.load()
        if len(nlp(sent).ents) > 0:
            return False
        else:
            return True
        
    def pronoun(sent):
        prons = ["she", "he", "his", "her", "i'll", "i ", "i've", "my", "we", "we've", "our"] 
        names = ["wayne", "sidney","elise", "william", "stephanie", "ricky"]
        questions = ["?", "who", "why", "how", "what", "laurine", "sid"]
        sent = sent.lower()
        for word in prons + names + questions:
            if word in sent:
                return False
        return True
    
    def is_english(sent):
        if detect(sent) == "en":
            return True
        return False
    
    if is_english(sent):
        if pronoun(sent):
            if name_entity(sent):
                return True
    return False


# Text Preprocessing
lemmatizer = WordNetLemmatizer()
def denoise_text(sent, stopwords_removal = False):
    def remove_punctuation(sent):
        """Remove_punctuation in a sentence"""
        return re.sub(r'[^\w\s]', '', sent)
    
    def remove_non_ascii(sent):
        """Remove sentences with non-ASCII characters""" 
        new_sent = unicodedata.normalize('NFKD', sent).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        
        return new_sent

    def strip_html(sent):
        """remove html"""
        soup = BeautifulSoup(sent, "html.parser")
        return soup.get_text()

    def remove_between_square_brackets(sent):
        """remove content in brackets"""
        return re.sub('\[[^]]*\]', '', sent)
    
    def stem_words(words):
        """Stem words in list of tokenized words"""
        stemmer = LancasterStemmer()
        stems = []
        for word in words:
            stem = stemmer.stem(word)
            stems.append(stem)
        return stems

    def lemmatize_verbs(words):
        """Lemmatize verbs in list of tokenized words"""
        lemmatizer = WordNetLemmatizer()
        lemmas = []
        for word in words:
            lemma = lemmatizer.lemmatize(word, pos='v')
            lemmas.append(lemma)
        return lemmas
    
    def remove_stopwords(words):
        stop_words = list(stopwords.words('english'))
        words = [item for item in words if item not in stop_words]
        return words
    
    sent = strip_html(sent)
    sent = remove_between_square_brackets(sent)
    sent = remove_punctuation(sent)
    words = nltk.word_tokenize(sent)
    words = lemmatize_verbs(words)
    if stopwords_removal:
        words = remove_stopwords(words)
    return " ".join(words)

def prep_text(raw_sents, stopwords_removal = False):
    new_sents = [denoise_text(raw_sents[i], stopwords_removal) for i in range(len(raw_sents))]
    for i in range(len(new_sents)-1, -1, -1):
        if new_sents[i] == "":
            del new_sents[i]
            del raw_sents[i]
    return raw_sents, new_sents