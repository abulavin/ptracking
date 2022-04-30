from collections import defaultdict
import re
from typing import List

from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from tqdm import tqdm

from ptracking.database import cursor

tag_map = defaultdict(lambda: wn.NOUN)
tag_map['J'] = wn.ADJ
tag_map['V'] = wn.VERB
tag_map['R'] = wn.ADV
tokenizer = RegexpTokenizer(r'\w+')


def combine_petition_contents(title, content):
    return title + ". " + content


def tokenize_words(text):
    text = text.lower()
    return tokenizer.tokenize(text)


def remove_stopwords(sent_tokens):
    return [
        word for word in sent_tokens if not word in stopwords.words('english')
    ]


def stem(sent_tokens):
    stemmer = PorterStemmer()
    return [stemmer.stem(word) for word in sent_tokens]


def lemmatise(sent_tokens):
    lemmatiser = WordNetLemmatizer()
    return [
        lemmatiser.lemmatize(token, tag_map[tag[0]])
        for token, tag in pos_tag(sent_tokens)
    ]


def _remove_short_words_and_numbers(text: List[str]) -> List[str]:
    return list(
        filter(lambda w: len(w) >= 3 and not re.match("[0-9]+", w), text))


def petition_preprocess(petition_title, petition_content, method='lemmatise'):
    if petition_title is not None:
        text = combine_petition_contents(petition_title, petition_content)
    else:
        text = petition_content

    text = tokenize_words(text)
    text = remove_stopwords(text)

    # Remove numbers and words less than 3 characters
    text = _remove_short_words_and_numbers(text)

    if method == 'lemmatise':
        text = lemmatise(text)
    elif method == "stem":
        text = stem(text)
    else:
        raise NotImplementedError(
            f"{method} is not a valid word stemming or lematising method.")

    return text


def update_processed_content():
    with cursor() as cur:
        cur.execute("SELECT petition_id, title, content FROM petition")
        res = cur.fetchall()

    updated = []
    for petition_id, title, content in tqdm(res):
        processed_text = petition_preprocess(title, content)
        updated.append((processed_text, petition_id))

    with cursor() as cur:
        cur.executemany(
            "UPDATE petition SET processed_content = %s WHERE petition_id = %s",
            updated)
