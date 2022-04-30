import unittest

from sklearn.neighbors import KNeighborsRegressor

from ptracking.predict import BaselinePredictor
import numpy as np


class TestBaseline(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        d_len = 10
        cls.lookup = {i: i * 10 for i in range(1, d_len + 1)}
        cls.petition_ids = sorted(list(cls.lookup.keys()))
        cls.labels = sorted(list(cls.lookup.values()))
        cls.model = BaselinePredictor(cls.lookup)
        cls.features = np.random.random_sample(size=(d_len, 5))

    def test_throws_on_empty_lookop(self):
        with self.assertRaises(ValueError):
            BaselinePredictor({})

    def test_can_fit(self):
        self.model.fit(self.features, self.petition_ids)
        self.assertIsNotNone(self.model.knn)
        self.assertIsNotNone(self.model.X_train)
        self.assertIsNotNone(self.model.y_train)

    def test_can_predict(self):
        self.model.fit(self.features, self.petition_ids)

        query = np.zeros(shape=(10, 5))
        prediction = self.model.predict(query)
        self.assertEqual(prediction.shape, (10, ))

        # Check the prediction is the mean of the 5 labels
        knn = KNeighborsRegressor(n_neighbors=self.model.k)
        knn.fit(self.features, self.labels)

        actual = knn.predict(query)
        self.assertListEqual(list(prediction), list(actual),
                             "baseline predictions do not match knn")

    def test_checks_array(self):
        self.model.fit(self.features, self.petition_ids)
        with self.assertRaises(ValueError) as exc:
            self.model.predict([0, 0, 0, 0, 0])
            msg = exc.exception.args
            self.assertIn("reshape", msg)
