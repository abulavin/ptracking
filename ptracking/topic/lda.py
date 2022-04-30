from typing import Dict, List

import gensim.corpora as corpora
import pandas as pd
from gensim.models import LdaMulticore, TfidfModel
from ptracking.database import Fetcher


def topics(num_topics: int = 10,
           tfidf_threshold=0.1,
           alpha=0.1,
           eta=0.1, gvmt_period='all') -> pd.DataFrame:
    documents = _fetch_petition_content(gvmt_period=gvmt_period)
    return _create_model(documents, num_topics, tfidf_threshold, alpha, eta)


def _fetch_petition_content(gvmt_period) -> Dict[int, List[str]]:
    """Extract the preprocessed text content of each petition from the database"""
    res = Fetcher.select_columns("processed_content", gvmt_period=gvmt_period)
    return res["processed_content"].to_dict()


def _create_model(documents: Dict[int, List[str]],
                  num_topics: int = 10,
                  tfidf_threshold=0.1,
                  alpha=0.1,
                  eta=0.1):
    processed_text = list(documents.values())
    dictionary = corpora.Dictionary(processed_text)

    # Create a separate corpus for TFIDF so we can filter out low value words
    tfidf_corpus = [dictionary.doc2bow(words) for words in processed_text]
    tfidf = TfidfModel(tfidf_corpus, dictionary)

    petition_dict = {}
    # Here we create a new corpus for LDA with the low value words removed from each documents BoW.
    lda_corpus = []
    for petition_id, text in documents.items():
        bow = dictionary.doc2bow(text)
        low_value_words = [
            id for id, value in tfidf[bow] if value < tfidf_threshold
        ]
        new_bow = [b for b in bow if b[0] not in low_value_words]
        lda_corpus.append(new_bow)
        petition_dict[petition_id] = new_bow

    # Build LDA model
    lda_model = fit_lda_model(lda_corpus, dictionary, num_topics, alpha, eta)
    rows = []
    for petition_id, bow in petition_dict.items():
        topics = lda_model.get_document_topics(bow, minimum_probability=0)
        rows.append((petition_id, *[prob for _, prob in topics]))

    columns = ["petition_id"] + ["topic_" + str(i) for i in range(num_topics)]
    df = pd.DataFrame(rows, columns=columns)
    df.set_index('petition_id', inplace=True)
    return df, lda_model


def fit_lda_model(corpus, id2word, n, alpha, eta) -> LdaMulticore:
    lda_model = LdaMulticore(corpus=corpus,
                             id2word=id2word,
                             num_topics=n,
                             alpha=alpha,
                             eta=eta)
    return lda_model
