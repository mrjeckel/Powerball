import numpy as np

from datetime import datetime as dt
from scipy import stats

class PowerballCleaner2015:
    """
    Normalizes data around the changes made to Powerball on Oct 04, 2015
    White balls 60-69 were added while Powerballs were reduced from 35 to 26
    """
    change_date = dt.strptime('10/04/2015', '%m/%d/%Y')
    missing_ball_range = np.arange(60, 70)
    powerball_limit = 26

    def __init__(self, winning_numbers):
        self.ball_numbers = self._clean_ball_numbers(winning_numbers)
        self.powerball_numbers = self._clean_powerball_numbers(winning_numbers)

    def _add_missing_balls(self, winning_numbers):
        # Filter all winners before the date and drop the powerball
        ball_numbers = winning_numbers.loc[:, :4].values.flatten()
        sliced_numbers = winning_numbers[winning_numbers.index <= self.change_date]
        sliced_ball_numbers = sliced_numbers.loc[:, :4].values.flatten()

        # Find the mode occurence and add missing numbers at that median
        _, frequency = np.unique(sliced_ball_numbers, return_counts=True)
        mode = int(stats.mode(frequency).mode)
        return np.append(ball_numbers, np.tile(self.missing_ball_range, mode))

    def _clean_ball_numbers(self, winning_numbers):
        return self._add_missing_balls(winning_numbers)

    def _remove_missing_powerballs(self, winning_numbers):
        powerball_numbers = winning_numbers.values.T[-1].flatten()
        mask = powerball_numbers <= self.powerball_limit
        return powerball_numbers[mask]

    def _clean_powerball_numbers(self, winning_numbers):
        return self._remove_missing_powerballs(winning_numbers)

    @classmethod
    def get_ball_and_powerball_arrays(cls, winning_numbers, draw_date):
        # TODO: unit testing to make sure data is getting cleaned properly
        ball_numbers = cls._add_missing_balls(winning_numbers)
        
        if draw_date >= cls.change_date:
            powerball_numbers = cls._remove_missing_powerballs
        else:
            powerball_numbers = winning_numbers.values.T[-1].flatten()

        return ball_numbers, powerball_numbers
    

class MegaMillionsCleaner2017:
    """
    Normalizes data around the changes made to MegaMillions on Oct 28, 2017
    White balls 71-75 were removed while Megaballs increased from 15 to 25
    """
    change_date = dt.strptime('10/28/2017', '%m/%d/%Y')
    ball_limit = 70
    missing_megaball_range = np.arange(71, 76)
