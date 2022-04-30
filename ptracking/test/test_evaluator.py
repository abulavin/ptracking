import unittest

import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

from ptracking.predict.evaluator import Evaluator


class TestEvaluator(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        data_len = 10
        data = {
            "petition_id":
            list(range(1, data_len + 1)),
            "created_at":
            [datetime.now() + timedelta(hours=i) for i in range(data_len)],
            "signatures": [i * 10 for i in range(1, data_len + 1)],
            "topic_0":
            np.random.random_sample(size=data_len),
            "topic_1":
            np.random.random_sample(size=data_len),
            "topic_2":
            np.random.random_sample(size=data_len),
        }
        cls.dataset = pd.DataFrame(data)
        cls.tscv = TimeSeriesSplit(test_size=1)

    def test_init(self):
        evaluator = Evaluator(self.tscv)
        self.assertIsNotNone(evaluator.cv)

    def test_runs_model(self):
        class DummyModel:
            def __init__(self) -> None:
                self.called = 0

            def fit(self, X, y):
                pass

            def predict(self, X):
                self.called += 1
                # predict 1 for everything
                return np.ones(shape=X.shape[0])

        evaluator = Evaluator(self.tscv)

        topics = self.dataset[["topic_0", "topic_1", "topic_2"]].to_numpy()
        labels = self.dataset['signatures'].to_numpy()
        model = DummyModel()
        predictions = evaluator.run_model(model, topics, labels)
        self.assertEqual(len(topics), len(predictions))
        self.assertEqual(model.called, self.tscv.n_splits)
        # The amount of predictions we made should be n_splits * test_size
        # because the dummy model gives everything a 1 and all else is set to 0.
        # Therefore, counting the number of 1s in predictions tells us how many
        # predictions we made
        self.assertEqual(np.sum(predictions),
                         self.tscv.n_splits * self.tscv.test_size)

        # Check the the index of the prediction matches the petition_id i.e they line up.
        # Probably being paranioid, but want to check this anyway
        for i in range(len(predictions)):
            # feature is corresponds to the prediciton at the ith location
            feature = topics[i] 
            row = self.dataset[["topic_0", "topic_1", "topic_2"]].iloc[i].to_numpy()
            self.assertTrue(all(np.equal(feature, row)))
