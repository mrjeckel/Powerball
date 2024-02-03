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

from analyzer import ProbabalisticModel


class TestProbabalisticModel(unittest.TestCase):
    BALL_DRAWS = [1, 1, 1, 2, 2, 3, 5, 5, 5, 6, 6, 7, 9, 9, 9]
    SINGLE_DRAWS = [1, 1, 4]

    def setUp(self):
        """ """
        self.model = ProbabalisticModel()
        self.model.BALL_RANGE = np.arange(1, 10)
        self.model.SINGLE_RANGE = np.arange(1, 5)

    def test_get_occurences(self):
        """ """
        ball_occurrences = self.model._get_occurrences(
            self.BALL_DRAWS, self.model.BALL_RANGE
        )
        np.testing.assert_array_equal(
            ball_occurrences, np.array([3, 2, 1, 0, 3, 2, 1, 0, 3])
        )

        single_occurrences = self.model._get_occurrences(
            self.SINGLE_DRAWS, self.model.SINGLE_RANGE
        )
        np.testing.assert_array_equal(single_occurrences, np.array([2, 0, 0, 1]))

    def test_basic_calculate_distribution(self):
        """ """
        ball_distribution, single_distribution = (
            self.model._calculate_normalized_distribution(
                self.BALL_DRAWS, self.SINGLE_DRAWS
            )
        )

        ball_probabilties = np.array(
            [
                0.00060938,
                0.00548446,
                0.04936015,
                0.44424132,
                0.00060938,
                0.00548446,
                0.04936015,
                0.44424132,
                0.00060938,
            ]
        )
        np.testing.assert_allclose(ball_distribution, ball_probabilties)

        single_probabilties = np.array([0.02702703, 0.43243243, 0.43243243, 0.10810811])
        np.testing.assert_allclose(single_distribution, single_probabilties)

    def test_realistic_calculate_distribution(self):
        """ """
        realistic_ball_freq = np.random.choice(np.arange(1, 1500), 10)
        raw_ball_distribution = self.model._calculate_raw_distribution(
            realistic_ball_freq
        )
        self.assertTrue(all(raw_ball_distribution > 0))

        realistic_ball_draws = np.random.choice(self.model.BALL_RANGE, 10000)
        realistic_single_draws = np.random.choice(self.model.SINGLE_RANGE, 10000)

        ball_distribution, single_distribution = (
            self.model._calculate_normalized_distribution(
                realistic_ball_draws, realistic_single_draws
            )
        )

        self.assertAlmostEqual(ball_distribution.sum(), 1.0)
        self.assertAlmostEqual(single_distribution.sum(), 1.0)
