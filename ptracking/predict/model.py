from abc import ABC, abstractmethod
from typing import Dict

import numpy as np
from sklearn.neighbors import KNeighborsRegressor
from sklearn.utils.validation import check_array, check_is_fitted, check_X_y


class PetitionModel(ABC):
    @abstractmethod
    def fit(self, X, y):
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        pass


class BaselinePredictor(PetitionModel):
    def __init__(self, signature_lookup: Dict[int, int], k=5):
        """The baseline predictor for generating k-NN based estimations of signature count
        
        Because the k-NN Model uses petition_id as a label, we must provide an auxilary dataset
        which allows us to look up signature counts (or other features) of petitions by ID
        """
        if len(signature_lookup) == 0:
            raise ValueError("signature lookup cannot be empty")
        self._lookup = signature_lookup
        self.k = k

    def fit(self, X, y):
        self.knn: KNeighborsRegressor = KNeighborsRegressor(n_neighbors=self.k,
                                                            n_jobs=-1)
        self.knn.fit(X, y)

        self.X_train = X
        self.y_train = y
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = check_array(X)

        _, indices = self.knn.kneighbors(X)

        matrix = []
        for n_vect in indices:
            p_ids = [self.y_train[i] for i in n_vect]
            s = [self._lookup[p] for p in p_ids]
            matrix.append(s)
        return np.mean(matrix, axis=1)

class Example(PetitionModel):
    """This is an example of how to implement a model for predicting signature count"""
    def __init__(self, k: int = 5) -> None:
        self._k = k

    def fit(self, X, y):
        # Check that X and y have correct shape
        X, y = check_X_y(X, y)
        self.clustering: KNeighborsRegressor = KNeighborsRegressor(
            self._k).fit(X, y)

        self.X_ = X
        self.y_ = y
        # Return the classifier
        return self

    def predict(self, X):
        # Check is fit had been called
        check_is_fitted(self)

        # Input validation
        X = check_array(X)

        return self.clustering.predict(X)

    def set_params(self, **params):
        return super().set_params(**params)
