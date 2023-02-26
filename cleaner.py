import numpy as np

from datetime import datetime as dt

class PowerballCleaner2015:
    """
    Normalizes data around the changes made to Powerball on Oct 04, 2015
    White balls 60-69 we added while Powerballs were reduced from 35 to 26
    """
    change_date = dt.strptime('10/04/2015', '%m/%d/%Y')
    # [,)
    missing_ball_range = np.arange(60, 70)
    powerball_limit = 26

    def __init__(self, winning_numbers):
        self.ball_numbers = self._clean_ball_numbers(winning_numbers)
        self.powerball_numbers = self._clean_powerball_numbers(winning_numbers)

    def _clean_ball_numbers(self, winning_numbers):
        normalized_winners = self._add_missing_before_date(winning_numbers, self.change_date)

        # Filter the winners that don't need to be modified then combine and return
        raw_winners = winning_numbers[winning_numbers.index >= self.change_date].values.T[:-1].flatten()
        return np.append(normalized_winners, raw_winners)

    def _add_missing_before_date(self, winning_numbers, date):
        # Filter all winners before the date and drop the powerball
        sliced_numbers = winning_numbers[winning_numbers.index < date]
        ball_numbers = sliced_numbers.values.T[:-1].flatten()

        # Find the median occurence and add missing numbers at that median
        _, frequency = np.unique(ball_numbers, return_counts=True)
        median = int(np.median(frequency))
        return np.append(ball_numbers, np.tile(self.missing_ball_range, median))

    def _clean_powerball_numbers(self, winning_numbers):
        powerball_numbers = winning_numbers.values.T[-1].flatten()
        mask = powerball_numbers <= self.powerball_limit
        return powerball_numbers[mask]
