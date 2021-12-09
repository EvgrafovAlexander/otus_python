import unittest

import log_analyzer


class TestLogAnalyzer(unittest.TestCase):

    def setUp(cls) -> None:
        cls.get_median_odd = [1, 3, 5, 4, 2]
        cls.get_median_even = [6, 3, 2, 4, 5, 1]

    def test_get_median_odd(self):
        result = log_analyzer.get_median(self.get_median_odd)
        self.assertEqual(result, 3)

    def test_get_median_even(self):
        result = log_analyzer.get_median(self.get_median_even)
        self.assertEqual(result, 3.5)


if __name__ == '__main__':
    unittest.main()
