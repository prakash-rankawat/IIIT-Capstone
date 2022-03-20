from bs4 import BeautifulSoup
import requests
import re
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
import nltk
from spellchecker import SpellChecker
from collections import Counter
from nltk.tokenize import TweetTokenizer
import numpy as np
import readability
import csv
import requests as r
from datetime import datetime
import time
import warnings
from urllib.parse import urljoin
from urllib.parse import urlparse

def feature_extract(url,save_flag=True):

    # Get the text of web page
    # instantiate a BeautifulSoup object
    source = requests.get(url).text
    soup = BeautifulSoup(source,"html.parser")

    # to find the Stylesheets
    # links = soup.find_all("link", {"rel":"stylesheet"})
    # numCSS = len(links)

    # strip all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    arr = soup.get_text(" ", strip=True).split('\n')

    # discard empty rows
    arr = list(filter(lambda x: len(x) > 0, arr))

    # remove leading traing white spaces
    arr = list(map(lambda x: x.strip(), arr))

    # Extract text
    text = ""
    for sentence in arr:
        text += sentence + " "

    # Text based features
    # token count
    tokens = len(text)

    # commas count
    commas = len(re.findall(',', text))

    # exclamations count
    exclamations = len(re.findall('!', text))

    # dots count
    dots = len(re.findall('\.', text))

    # questions count
    questions = len(re.findall("\?", text))

    # polarity
    text_blob = TextBlob(text)
    polarity = text_blob.sentiment.polarity

    # split long sentences into short sentences based on '.'
    arr = list(map(lambda x: x.split('.'), arr))

    # convert 2D list into 1D list
    sentences_list = list()
    for sentences_array in arr:
        sentences_list += list(filter(lambda x: len(x) > 0, sentences_array))

    positive_sentences = 0
    negative_sentences = 0
    subjective_sentences = 0
    objective_sentences = 0

    for sentence in sentences_list:
        sent = TextBlob(sentence)
        polarity = sent.sentiment.polarity
        subjectivity = sent.sentiment.subjectivity

        if polarity > 0.0:
            positive_sentences += 1
        else:
            negative_sentences += 1

        if subjectivity >= 0.3:
            subjective_sentences += 1
        else:
            objective_sentences += 1

    text_new = ""
    for word in text.split(" "):
        word = re.sub(r'[^a-zA-Z]', '', word)
        text_new += word + " "

    # spelling errors count
    spell = SpellChecker()
    spelling_errors = 0
    for word in text_new.split(" "):
        correct_word = spell.correction(word)
        if not word == correct_word:
            spelling_errors += 1

    # Entropy(text_complexity)
    tokenizer = TweetTokenizer()
    tokens = tokenizer.tokenize((text))
    num_tokens = len(tokens)
    word_hist = Counter([token for token in tokens])

    entropy_sum = 0
    for word, count in word_hist.items():
        entropy_sum += (count * (np.math.log10(num_tokens) - np.math.log10(count)))
    text_complexity = (1 / num_tokens) * entropy_sum

    results = readability.getmeasures(text, lang='en')
    results['readability grades']
    smog = results['readability grades']['SMOGIndex']

    # POS Tagging
    # 'Noun' : 'NN',
    # 'Verb' : 'VB',
    # 'Adjective' : 'JJ',
    # 'Adverb' : 'RB',
    # 'Determiner' : 'DT'

    # JJ	adjective	'big'
    # JJR	adjective, comparative	'bigger'
    # JJS	adjective, superlative	'biggest'
    # NN	noun, singular 'desk'
    # NNS	noun plural	'desks'
    # NNP	proper noun, singular	'Harrison'
    # NNPS	proper noun, plural	'Americans'
    # VB	verb, base form	take
    # VBD	verb, past tense	took
    # VBG	verb, gerund/present participle	taking
    # VBN	verb, past participle	taken
    # VBP	verb, sing. present, non-3d	take
    # VBZ	verb, 3rd person sing. present	takes
    # RB	adverb	very, silently,
    # RBR	adverb, comparative	better
    # RBS	adverb, superlative	best

    # count number of nouns, verbs, adjectives, adverbs, determiners
    for sentence in sentences_list:
        text = nltk.word_tokenize(sentence)
        list_of_tags = nltk.pos_tag(text)
        NN = 0
        VB = 0
        JJ = 0
        RB = 0
        DT = 0

    for tag_tuple in list_of_tags:
        tag = tag_tuple[1]
        if (tag in ['NN', 'NNS', 'NNP', 'NNPS']):
            NN += 1
        elif (tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']):
            VB += 1
        elif (tag in ['JJ', 'JJR', 'JJS']):
            JJ += 1
        elif (tag in ['RB', 'RBR', 'RBS']):
            RB += 1
        elif (tag == 'DT'):
            DT += 1

    # To get Alexa-Rank of URL
    alex_url = "https://www.alexa.com/siteinfo/" + url
    alex_respone = r.get(alex_url)  # get information from page
    alex_soup = BeautifulSoup(alex_respone.content, 'html.parser')
    for match in alex_soup.find_all('span'):  # remove all span tag
        match.unwrap()
    global_rank = alex_soup.select('p.big.data')  # select any p tag with big and data class
    global_rank = str(global_rank[0])
    res = re.findall(r"([0-9,]{1,12})", global_rank)  # find rank
    alexa_rank = res[0]

    # To get domain name of a URL
    get_domain = urlparse(url).netloc
    document_url_y = '.'.join(get_domain.split('.')[-1:])

    if (save_flag == True):
        # open the file in the write mode
        with open('url_features.csv', 'a', newline='') as csvfile:
            # csv header
            #            header = ['token_count','commas_count','exclamations_count','dots_count','questions_count',
            #                       'polarity','positive_sentences_count','negative_sentences_count',
            #                       'subjective_sentences_count','objective_sentences_count',
            #                       'spelling_errors_count','text_complexity','smog',
            #                       'noun_count','verb_count','adj_count','deter_count']
            data = [
            url, token,commas, exclamations, dots, questions,
                polarity, positive_sentences, negative_sentences,
                subjective_sentences, objective_sentences,
                spelling_errors, text_complexity, smog,
                NN, VB, JJ, RB, DT, alexa_rank, document_url_y
            ]
            # create the csv writer
            writer = csv.writer(csvfile)
            # write header & a row to the csv file
            # writer.writerow(header)
            writer.writerow(data)

    feature_list = [
        tokens, commas, exclamations, dots, questions,
        polarity, positive_sentences, negative_sentences,
        subjective_sentences, objective_sentences,
        spelling_errors, text_complexity, smog,
        NN, VB, JJ, RB, DT, alexa_rank, document_url_y
    ]

    return feature_list