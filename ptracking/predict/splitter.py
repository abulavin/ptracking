from ptracking.predict.evaluator import Splitter

class WindowGenerator(Splitter):
    def __init__(self,
                 overlap: bool = True,
                 number_of_windows: int = None,
                 points_per_window: int = None) -> None:

        if number_of_windows and points_per_window:
            # TODO log
            print(
                "number_of_windows and points_per_window both set - falling back to number_of_windows."
            )
        elif number_of_windows is None and points_per_window is None:
            raise ValueError(
                "exactly one of number_if_windows and points_per_window must be set"
            )
        elif number_of_windows == 0:
            raise ValueError("number_of_windows cannot be 0")
        elif points_per_window == 0:
            raise ValueError("points_per_window cannot be 0")
        self._number_of_windows = number_of_windows
        self._points_per_window = points_per_window
        self._overlap = overlap

    # def split(self, X) -> Generator[Iterable]:
    #     # TODO refactor this
    #     n = len(X)
    #     if self._overlap:
    #         if self._points_per_window is None:
    #             self._points_per_window = n - self._number_of_windows + 1
    #         elif self._number_of_windows is None:
    #             self._number_of_windows = n - self._points_per_window + 1
    #         for i in range(self._number_of_windows):
    #             yield self._X[i:i + self._points_per_window], [i:i + self._points_per_window]
    #     else:
    #         # if we're not sliding we will discard the last items
    #         if self._points_per_window is None:
    #             self._points_per_window = n // self._number_of_windows
    #         elif self._number_of_windows is None:
    #             self._number_of_windows = n // self._points_per_window
    #         for i in range(self._number_of_windows):
    #             lower = i * self._points_per_window
    #             upper = min(lower + self._points_per_window, n)
    #             yield self._X[lower:upper], self._y[lower:upper]
