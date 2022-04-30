import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generator, List, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ptracking.database.database import ColumnFetcher, Fetcher
from ptracking.predict.model import PetitionModel

__all__ = ["WindowGenerator", "Splitter", "Dataset", "Plotter"]

DEFAULT_BINS = [0, 10, 100, 1000, 10_000, 100_000, 1_000_000, 10_000_000]


class Dataset:
    def __init__(self, fetcher: ColumnFetcher = Fetcher.select_columns) -> None:
        """Use dependency injection to specify the function which retrieves data and
        its associated columns from a source, such as the database
        """
        self._fetcher = fetcher

    def prepare(
        self,
        columns: List[str],
        bins: List[int] = DEFAULT_BINS,
    ) -> pd.DataFrame:
        """"Return a Pandas Dataframe indexed by petition_id containing `columns`
        for each petition.
        
        The resulting dataframe has two columns included by default:
        "signatures" - the signature count corresponding to each petition
        "class" - the integer index of the bin that the signature count falls into.
        For example, for bins of 0, 100, 1000, a petition with 50 signatures would
        have class 1, and 150 signatures would have class 2.
        """
        dataset = self._fetcher("signatures", *columns)
        dataset['class'] = pd.cut(dataset.signatures,
                                  bins,
                                  include_lowest=True,
                                  labels=False)
        dataset['class'] += 1
        return dataset


class Splitter(ABC):
    """Interface for objects which create 'sliding window' verification datasets"""
    @abstractmethod
    def split(self, X) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        pass


class Evaluator:
    def __init__(self, cv: Splitter):
        self.cv = cv
        self.predictions = None

    def run_model(self, model: PetitionModel, features: np.ndarray,
                  labels: np.ndarray) -> np.ndarray:
        """Run a model using `features` and `labels` as the dataset
        
        Parameters
        ---
        model: a model implementing `predict(X) and `fit(X, y)`
        methods.
        features: np.ndarray, matrix of feature vectors
        labels: np.ndarray, vector of labels (signature counts)

        Returns
        ---
        The predicted signature count for each feature vecto in `features`
        Vectors which are not used for prediction (training only) are given
        the label 0.

        """
        predictions = np.zeros(shape=len(features)).reshape(-1, 1)
        for train_idx, test_idx in self.cv.split(features):
            X_train, y_train = features[train_idx], labels[train_idx]
            X_test = features[test_idx]

            model.fit(X_train, y_train)
            prediction = model.predict(X_test)
            predictions[test_idx] = prediction.reshape(-1, 1)
        self.predictions = predictions
        return predictions


class Plotter:
    """Figure plotter for the results of validating a model"""
    def __init__(self, petition_ids_index: pd.Index) -> None:
        """
        Parameters
        ---
        petition_ids_index: a dataframe index of petition_ids.
        """
        self._index = petition_ids_index

    def plot_results(self,
                     predictions,
                     actual,
                     dates,
                     filter_after: str = None):
        prediction_df = pd.DataFrame(
            {
                'y_pred': predictions,
                'y_true': actual,
                'created_at': dates,
            },
            index=self._index)

        if self._date_str_valid(filter_after):
            prediction_df = prediction_df[prediction_df.created_at > datetime.
                                          strptime(filter_after, "%Y-%m-%d")]

        _, ax = plt.subplots(sharex=True, figsize=(16, 9))
        ax.plot(prediction_df.created_at,
                prediction_df.y_true,
                label="Actual Signatures")
        ax.plot(prediction_df.created_at,
                prediction_df.y_pred,
                label="Predicted Signatures")
        ax.legend()
        plt.tight_layout()

    def _date_str_valid(self, datestr: Union[str, None]) -> bool:
        if datestr:
            if not re.match(r"\d{4}-\d{2}-\d{2}", datestr):
                raise ValueError(
                    f"Date string must match form YYYY-MM-DD: {datestr}")
            return True
        return False
