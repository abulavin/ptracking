import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from nltk.parse import CoreNLPParser
from ptracking.database import Fetcher



PICKLE_PATH = Path(__file__).absolute().parent


def add_whitespace_after_fullstop(text):
    text = text.strip().split(" ")
    new_text = []
    for word in text:
        if "." in word:
            before, dot, after = word.partition(".")
            if after and before.isalpha() and after[0].isalpha():
                word = before + dot + " " + after
        new_text.append(word)

    return " ".join(new_text)


def get_sentiment(server: CoreNLPParser, text):
    result = server.api_call(text,
                             properties={
                                 'annotators': 'sentiment',
                                 'outputFormat': 'json',
                             },
                             timeout=50000)
    # 0 = v negative, 1 = negative, 2 = neutral, 3 = positive, 4 = v postive
    scores = [int(s["sentimentValue"]) for s in result["sentences"]]
    return [np.mean(scores), np.std(scores), min(scores), max(scores)]


def sentiment_scores(petition_id=0, url='http://localhost:9000'):
    data = Fetcher.select_columns("content")
    data = data[data.index > petition_id]
    print("Fetched petition data")
    nlp = CoreNLPParser(url=url)

    for petition_id, text in zip(data.index, data.content):
        text = add_whitespace_after_fullstop(text)
        yield petition_id, get_sentiment(nlp, text)


def sentiment(recompute=False) -> pd.DataFrame:
    results_path = PICKLE_PATH.joinpath("sentiment.pkl")

    if not recompute and os.path.isfile(results_path):
        return pd.read_pickle(results_path)

    data, max_id = _read_pickle(results_path)
    rows = []
    count = 0
    for petition_id, scores in sentiment_scores(max_id):
        count += 1
        rows.append([petition_id, *scores])
    df = pd.DataFrame(rows, columns=data.columns)
    data.append(df)
    data.to_pickle(results_path)
    return data


def ner() -> pd.DataFrame:
    pkl_loc = PICKLE_PATH.joinpath("ner.pkl")
    if os.path.isfile(pkl_loc):
        return pd.read_pickle(pkl_loc)
    data = []

    for entities in get_named_entities():
        data.append(entities)

    df = pd.DataFrame(data)
    df.set_index("petition_id", inplace=True)
    df.to_pickle(pkl_loc)
    return df


def get_named_entities(url="http://localhost:9000"):
    data = Fetcher.select_columns("content")
    print("Fetched Petition Data")
    nlp = CoreNLPParser(url=url)

    for petition_id, text in zip(data.index, data.content):
        text = add_whitespace_after_fullstop(text)
        counts = ner_api_call(nlp, text)
        counts['petition_id'] = petition_id
        yield counts


def ner_api_call(server: CoreNLPParser, text):
    result = server.api_call(text,
                             properties={
                                 'annotators': 'ner',
                                 'outputFormat': 'json'
                             },
                             timeout=5000)
    counts = defaultdict(int)
    for sentence in result['sentences']:
        for entity in sentence['entitymentions']:
            label = entity['ner']
            counts[label] += 1
    return counts


def _read_pickle(path: Path):
    if os.path.isfile(path):
        data: pd.DataFrame = pd.read_pickle(path)
        if len(data) == 0:
            max_id = 0
        else:
            max_id = data.petition_id.max()
    else:
        data: pd.DataFrame = pd.DataFrame(
            [], columns=["petition_id", "mean", "std", "min", "max"])
        max_id = 0
    return data, max_id


if __name__ == "__main__":
    arg = sys.argv[1]
    if arg == "sentiment":
        df = sentiment(recompute=True)
    elif arg == "ner":
        df = ner()
    else:
        print("Usage: corenlp.py \{sentiment | ner\}")

