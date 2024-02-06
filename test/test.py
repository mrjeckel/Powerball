"""
ball
-----------------------------------
69 has never been drawn
1 has been drawn 8 times
2, 3, 4, 5 have been drawn 5 times
65, 66, 67, 68 have been drawn once
everything else 1-69 has been drawn twice

powerball
--------------------------------
26 has never been drawn
1 has been drawn 3 times
everything else 1-29 has been drawn once
"""

import unittest
import numpy as np
import pandas as pd

from analyzer import ProbabalisticModel


class TestProbabalisticModel(unittest.TestCase):
    """ """

    def setUp(self):
        """ """

        self.model = ProbabalisticModel()
        self.ball_draws_df = pd.read_csv("data/encoded_ball_draws.csv")
        self.ball_draws_df.columns = self.ball_draws_df.columns.astype(int)

    def _validate_last_distribution(self, ball_distribution):
        """
        Check for wrapping, truncating, and a sum of 1
        """

        self.assertTrue(all(ball_distribution.iloc[-1][-5:] >= 0))
        self.assertTrue(all(ball_distribution.iloc[-1][-5:] != 0))
        self.assertAlmostEqual(ball_distribution.iloc[-1].sum(), 1.0)

    def test_distribution(self):
        """
        Test that calculated distribution probabilities match precalculated probabilities
        """

        ball_distribution, _ = self.model._calculate_normalized_distribution(
            self.ball_draws_df
        )
        np.testing.assert_allclose(
            ball_distribution.iloc[-1][-5:], [4.407356788820851401e-19] * 5
        )
        self._validate_last_distribution(ball_distribution)

    def test_long_distribution(self):
        """
        Test that distribution keeps very small numbers when a single draw occurrs continuously
        """

        repeated_ball_draws = pd.concat([self.ball_draws_df] * 10, ignore_index=True)
        ball_distribution, _ = self.model._calculate_normalized_distribution(
            repeated_ball_draws
        )
        self._validate_last_distribution(ball_distribution)
