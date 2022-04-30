import multiprocessing
import os
import time
from multiprocessing import Pool, cpu_count
from typing import Callable, List, NamedTuple, Tuple, Union

import gensim.corpora as corpora
import numpy as np
import pandas as pd
from gensim.models import CoherenceModel, LdaModel, TfidfModel
from ptracking import ROOT_DIR
from ptracking.database import cursor
from ptracking.topic.ldamallet import LdaMallet


class Hyperparams(NamedTuple):
    """Hyperparams represents a point in in the hyperparamter search space"""
    tfidf_threshold: float
    num_topics: int
    alpha: float
    beta: float


class TrainResult(NamedTuple):
    """Train result contains the outcomes of successfully training an LDA model"""
    model: Union[LdaMallet, LdaModel]
    tfidf_threshold: float
    words_removed: int
    train_time_sec: float


class ModelRunner:
    """The Model runner enapsulates all the state and variables needed
    by processes to train an LDA model in parallel
    
    Attributes
    ---

    model - The class of the model used for training i.e. LdaMallet or LdaModel
    total_words: int. The total number of words in the corpus
    
    """
    def __init__(self, model: Union[LdaMallet,
                                    LdaModel], dictionary: corpora.Dictionary,
                 texts: List[List[str]]) -> None:
        """Initialise a model runner with state and variables required by child processes.
        This constructor unitialises the TFIDF model later used for filtering.

        Parameters
        ---
        model: LdaMallet | LdaModel. The class of the model to run. 
            Should have the same constructor interface
        
        dictionary: corpora.Dictionary. Corpus dictionary (already preprocessed, ideally).

        texts: List[List[str]]. The preprocessed texts of each petition.
        """
        self.model = model
        self._dict = dictionary
        self._texts = texts
        self._bow_corpus = []
        self.total_words = 0
        for words in texts:
            bow = dictionary.doc2bow(words)
            self._bow_corpus.append(bow)
            self.total_words += sum(val for _, val in bow)
        self._tfidf = TfidfModel(self._bow_corpus, self._dict)

    def run_model(self, thresh, num_topics, alpha, beta) -> TrainResult:
        """Train an LDA Model and return the result
        
        Parameters
        ---
        thresh: float. TFIDF threshold for filtering out common terms
        num_topics: int. number of topics to fit in the LDA model
        alpha: float. alpha hyperparameter of the LDA model. 
            Controls the per-document topic distribution
        beta: float. beta hyperparameter of the LDA model. Controls the per-topic
        term distribution

        Returns
        ---
        result: TrainResult. Contains the trained model, the TFIDF threshold used, 
        the number of terms removed due to TFIDF and the time taken in seconds to
        train the model. Note: the time taken as measured here differs from the time
        displayed by the stdout of Mallet, so the time here includes Java process 
        creation overhead.

        """
        lda_corpus, terms_removed = self._lda_corpus(thresh)
        start = time.time()
        lda_model = self.model(corpus=lda_corpus,
                               id2word=dictionary,
                               num_topics=num_topics,
                               alpha=alpha,
                               eta=beta,
                               random_state=100)
        train_time_s = time.time() - start
        return TrainResult(lda_model, thresh, terms_removed, train_time_s)

    def _lda_corpus(self,
                    thresh: float) -> Tuple[List[List[Tuple[int, int]]], int]:
        """Create a corpus for training the LDA model by filtering out all terms with
        a TFIDF score strictly less than `thresh`
        
        Parameters
        ---
        thresh: float. The TFIDF score threshold for which any words that have a 
        score strictly less than thresh are removed from the corpus.

        Returns
        ---

        lda_corpus: List[List[Tuple[int, int]]]. BoW corpus ready for LDA
        removed_words: int. The number of words (non-unique) removed from 
        the original corpus
        """
        lda_corpus = []
        removed_words = 0
        for bow in self._bow_corpus:
            low_value_words = {
                id
                for id, value in self._tfidf[bow] if value < thresh
            }
            new_bow = []
            for id, count in bow:
                if id in low_value_words:
                    removed_words += count
                else:
                    new_bow.append((id, count))
            lda_corpus.append(new_bow)
        return lda_corpus, removed_words


def fetch_processed_text() -> List[List[str]]:
    with cursor() as cur:
        cur.execute(
            "SELECT processed_content FROM petition WHERE state = 'closed'")
        content = cur.fetchall()

    return [text for (text, ) in content]


def generate_hyperparameters() -> List[Hyperparams]:
    """"Generate the LDA hyperparameter search space. This includes the TFIDF threshold"""
    params = []
    for thresh in np.linspace(0.0, 1.0, int(1 / 0.05) + 1):
        for num_topics in range(5, 30, 1):
            for alpha in np.linspace(0.05, 1.0, int(1 / 0.05)):
                for beta in np.linspace(0.05, 1.0, int(1 / 0.05)):
                    params.append(Hyperparams(thresh, num_topics, alpha, beta))
    return params


def run_workers(run_func: Callable[[List[Hyperparams]], TrainResult],
                params: List[Hyperparams]) -> List[TrainResult]:
    with multiprocessing.Pool(processes=cpu_count()) as pool:
        results = pool.map(run_func, params)
    return results


if __name__ == "__main__":
    text = fetch_processed_text()
    dictionary = corpora.Dictionary(text)

    params = generate_hyperparameters()

    runner = ModelRunner(LdaModel, dictionary, text)

    # worker is a closure which captures the runner
    # and allows us to monitor the current process PID
    def worker(params: Hyperparams):
        pid = os.getpid()
        print(
            (f"Process {pid} running with values topics={params.num_topics} "
             f"thresh={params.tfidf_threshold} alpha={params.alpha}, "
             f"beta={params.beta}"))
        return runner.run_model(thresh=params.tfidf_threshold,
                                num_topics=params.num_topics,
                                alpha=params.alpha,
                                beta=params.beta)

    # Here we fan out and fan in - child processes train a model using
    # a single set of hypeparameters and return the result.
    # This includes the model itself.
    results = run_workers(worker, params)

    rows = []
    for result in results:
        model = result.model
        # We can't run CoherenceModel in a child process because
        # CoherenceModel spawns its own child processes.
        # I.e. we can't have children spawing children
        coherencemodel = CoherenceModel(model=model,
                                        texts=text,
                                        dictionary=dictionary,
                                        coherence='c_v')

        coh = coherencemodel.get_coherence()
        rows.append({
            "tfidf_threshold": result.tfidf_threshold,
            "num_topics": model.num_topics,
            "alpha":
            model.alpha,  # Sometimes this an array of length num_topics
            "beta": model.eta,
            "total_words": runner.total_words,
            "terms_removed": result.words_removed,
            "train_time_s": result.train_time_sec,
            "topic_coherence": coh
        })
    df = pd.DataFrame(rows)
    write_path = ROOT_DIR.joinpath("hyperparams.pkl")
    df.to_pickle(write_path)
