# import unittest
# from ptracking.predict.splitter import WindowGenerator

# class TestWindowGenerator(unittest.TestCase):
#     def test_raises_on_no_data(self):
#         X = []
#         y = []
#         self.assertRaises(ValueError, WindowGenerator, X, y, 100)

#     def test_raises_on_missing_params(self):
#         X = [1, 2, 3]
#         y = [100, 10, 1]
#         self.assertRaises(ValueError, WindowGenerator, X, y)

#     def test_logs_fallback(self):
#         X = [1, 2, 3]
#         y = [100, 10, 1]
#         with self.assertLogs(level="INFO") as cm:
#             WindowGenerator(X, y, 100, 100)
#         self.assertEqual(cm.output, [
#             'WARNING:root:number_of_windows and points_per_window both set - falling back to number_of_windows.'
#         ])

#     def test_get_number_of_windows(self):
#         dataset = list(range(0, 10))
#         max_windows = len(dataset)
#         for windows in range(1, max_windows + 1):
#             generated = WindowGenerator(
#                 dataset, number_of_windows=windows).get(overlap=False)
#             seen = set()
#             n_windows = 0
#             for w in generated:
#                 n_windows += 1
#                 n = len(w)
#                 self.assertTrue(n > 0, "empty window")
#                 self.assertTrue(n == (len(dataset) // windows),
#                                 f"bad number of points in window: {n}")

#                 self.assertTrue(all(p not in seen for p in w),
#                                 "duplicates in set of items from windows")
#                 seen.update(w)
#             self.assertEqual(n_windows, windows)
#             # Check we have seen all our datapoints if we can
#             # divide all our points into the number of windows
#             if len(dataset) % windows == 0:
#                 self.assertSetEqual(seen, set(dataset))

#     def test_get_points_per_window(self):
#         dataset = list(range(0, 10))
#         max_points = len(dataset)
#         for points in range(1, max_points + 1):
#             generated = WindowGenerator(
#                 dataset, points_per_window=points).get(overlap=False)
#             seen = set()
#             for w in generated:
#                 n = len(w)
#                 self.assertTrue(n > 0, "empty window")
#                 self.assertTrue(n == points)
#                 self.assertTrue(all(p not in seen for p in w),
#                                 "duplicates in set of items from windows")
#                 seen.update(w)
#             # Check we have seen all our datapoints if we can
#             # divide all our points into evenly-sized windows
#             if len(dataset) % points == 0:
#                 self.assertSetEqual(seen, set(dataset))

#     def test_get_number_of_windows_sliding(self):
#         dataset = list(range(0, 10))
#         max_windows = len(dataset)
#         for windows in range(1, max_windows + 1):
#             generated = WindowGenerator(
#                 dataset, number_of_windows=windows).get(overlap=True)
#             seen = set()
#             n_windows = 0
#             for w in generated:
#                 n_windows += 1
#                 n = len(w)
#                 self.assertTrue(n > 0, "empty window")
#                 self.assertTrue(n == len(dataset) - windows + 1,
#                                 f"bad number of points in window: {n}")
#                 seen.update(w)
#             self.assertEqual(n_windows, windows)
#             self.assertSetEqual(seen, set(dataset))

#     def test_get_points_per_window_sliding(self):
#         dataset = list(range(0, 10))
#         max_points = len(dataset)
#         for points in range(1, max_points + 1):
#             generated = WindowGenerator(
#                 dataset, points_per_window=points).get(overlap=True)
#             seen = set()
#             for w in generated:
#                 n = len(w)
#                 self.assertTrue(n > 0, "empty window")
#                 self.assertTrue(n <= points)
#                 seen.update(w)
#             self.assertSetEqual(seen, set(dataset))
