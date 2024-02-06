from typing import Union

import numpy as np
import pandas as pd
from datetime import datetime as dt


class PowerballCleaner2015:
    """
    Normalizes data around the changes made to Powerball on Oct 04, 2015
    White balls 60-69 were added while Powerballs were reduced from 35 to 26
    """

    BALL_COLUMNS = np.arange(0, 5)
    SINGLE_INDEX = 5
    CHANGE_DATE = dt.strptime("10/07/2015", "%m/%d/%Y")
    MISSING_BALL_RANGE = np.arange(60, 70)
    SINGLE_LIMIT = 26

    @staticmethod
    def _one_hot_encode(
        winning_numbers: Union[pd.DataFrame, pd.Series]
    ) -> pd.DataFrame:
        """
        One-hot encode all ball numbers to columns with 0/1 for draws per date index
        """
        if isinstance(winning_numbers, pd.DataFrame):
            encoded_numbers = pd.get_dummies(winning_numbers[0], dtype=int)
            for column in winning_numbers.columns[1:]:
                encoded_column = pd.get_dummies(winning_numbers[column], dtype=int)
                encoded_numbers[encoded_column == True] = 1
        else:
            encoded_numbers = pd.get_dummies(winning_numbers, dtype=int)

        return encoded_numbers

    @classmethod
    def _add_missing_balls(cls, winning_numbers):
        """
        Add draws for the balls added after the change date
         Each missing ball is added at a frequency of the mode of draws prior to the change date
        """
        winning_numbers.loc[cls.CHANGE_DATE - pd.Timedelta(1, "d")] = 0
        winning_numbers.loc[
            winning_numbers.index < cls.CHANGE_DATE, cls.MISSING_BALL_RANGE
        ] = np.nan

        return winning_numbers.sort_index()

    @classmethod
    def _remove_missing_singles(cls, single_numbers):
        """
        Remove single draws after the change date by setting their values to np.nan
        """
        single_numbers.loc[
           single_numbers.index >= cls.CHANGE_DATE, single_numbers.columns > cls.SINGLE_LIMIT
        ] = np.nan
        return single_numbers

    @classmethod
    def get_ball_and_powerball_arrays(cls, winning_numbers):
        """
        Clean the winning numbers with respect to the game format changes
        """
        # TODO: unit testing to make sure data is getting cleaned properly
        encoded_ball = cls._one_hot_encode(winning_numbers[cls.BALL_COLUMNS])
        encoded_single = cls._one_hot_encode(winning_numbers[cls.SINGLE_INDEX])

        ball_draws = cls._add_missing_balls(encoded_ball)
        single_draws = cls._remove_missing_singles(encoded_single)

        return ball_draws, single_draws


class MegaMillionsCleaner2017:
    """
    Normalizes data around the changes made to MegaMillions on Oct 28, 2017
    White balls 71-75 were removed while Megaballs increased from 15 to 25
    """

    change_date = dt.strptime("10/28/2017", "%m/%d/%Y")
    ball_limit = 70
    missing_megaball_range = np.arange(71, 76)
