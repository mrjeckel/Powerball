import numpy as np

from datetime import datetime as dt
from scipy import stats


class PowerballCleaner2015:
    """
    Normalizes data around the changes made to Powerball on Oct 04, 2015
    White balls 60-69 were added while Powerballs were reduced from 35 to 26
    """

    change_date = dt.strptime("10/04/2015", "%m/%d/%Y")
    missing_ball_range = np.arange(60, 70)
    powerball_limit = 26

    @classmethod
    def _add_missing_balls(cls, winning_numbers):
        """
        Add draws for the balls added after the change date
         Each missing ball is added at a frequency of the mode of draws prior to the change date
        """
        ball_numbers = winning_numbers.loc[:, :4].values.flatten()
        sliced_numbers = winning_numbers[winning_numbers.index <= cls.change_date]
        sliced_ball_numbers = sliced_numbers.loc[:, :4].values.flatten()

        _, frequency = np.unique(sliced_ball_numbers, return_counts=True)
        mode = int(stats.mode(frequency).mode)
        return np.append(ball_numbers, np.tile(cls.missing_ball_range, mode))

    @classmethod
    def _remove_missing_powerballs(cls, winning_numbers):
        """
        Remove powerball draws that are not within the current range
        """
        powerball_numbers = winning_numbers.values.T[-1].flatten()
        mask = powerball_numbers <= cls.powerball_limit
        return powerball_numbers[mask]

    @classmethod
    def get_ball_and_powerball_arrays(cls, winning_numbers):
        """
        Clean the winning numbers with respect to the game format changes

        Returns:
            Flattened arrays of all draws for balls and powerballs
        """
        # TODO: unit testing to make sure data is getting cleaned properly
        ball_numbers = cls._add_missing_balls(winning_numbers)
        powerball_numbers = cls._remove_missing_powerballs(winning_numbers)

        return ball_numbers, powerball_numbers


class MegaMillionsCleaner2017:
    """
    Normalizes data around the changes made to MegaMillions on Oct 28, 2017
    White balls 71-75 were removed while Megaballs increased from 15 to 25
    """

    change_date = dt.strptime("10/28/2017", "%m/%d/%Y")
    ball_limit = 70
    missing_megaball_range = np.arange(71, 76)
