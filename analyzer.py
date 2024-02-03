import sqlalchemy as db
import numpy as np
from typing import Tuple

from sqlalchemy.orm import Session
from pandas import DataFrame, to_datetime
from models import LotteryDraw
from cleaner import PowerballCleaner2015, MegaMillionsCleaner2017


class Analyzer:
    def __init__(self, model):
        self.engine = db.create_engine(self.DB_ADDRESS)
        self.winning_numbers = self._read_all_winning_numbers()
        self.ball_draws, self.single_draws = self.cleaner.get_ball_and_powerball_arrays(
            self.winning_numbers
        )
        self.model = model()

    def _read_all_winning_numbers(self):
        with Session(bind=self.engine) as sess:
            query = sess.query(
                LotteryDraw.date, LotteryDraw.numbers, LotteryDraw.single
            ).all()
            dates = to_datetime([result[0] for result in query])
            stored_numbers = [
                (*result[1].strip("[]").split(", "), result[2]) for result in query
            ]

        return DataFrame(data=stored_numbers, index=dates).astype(int)

    def train(self):
        """ """
        self.model.train(self.ball_draws, self.single_draws)

    def predict(self):
        """ """
        top_balls, top_single = self.model.predict(self.cleaner.winning_numbers)
        return f"{top_balls} : {top_single}"


class ProbabalisticModel:
    """ """

    def _get_occurrences(
        self, draws: np.ndarray[int], draw_range: np.ndarray[int]
    ) -> np.ndarray[int]:
        """
        Returns draw frequency array populated with 0's for missing draws
        """
        array, frequency = np.unique(draws, return_counts=True)

        missing_indices = np.where(np.isin(draw_range, array, invert=True))[0]

        # Map range index to ball_array index
        missing_indices -= np.arange(missing_indices.size)

        # TODO: unit test the proper filling of 0s
        return np.insert(frequency, missing_indices, 0)

    @staticmethod
    def _calculate_raw_distribution(
        frequency: np.ndarray[int],
    ) -> np.ndarray[np.double]:
        """ """
        return 1 / np.power(frequency.size, frequency, dtype=np.longdouble)

    def _calculate_normalized_distribution(
        self, ball_draws: np.ndarray[int], single_draws: np.ndarray[int]
    ) -> Tuple[np.ndarray[np.double], np.ndarray[np.double]]:
        """
        Returns a normalized probability distribution
         Probability is first calculated by V = 1 / Size^N
          Then normalized by V / V.Sum
        """
        ball_frequency = self._get_occurrences(ball_draws, self.BALL_RANGE)
        single_frequency = self._get_occurrences(single_draws, self.SINGLE_RANGE)

        # TODO: this bit is in dire need of unit testing due to float wrapping
        ball_tmp = self._calculate_raw_distribution(ball_frequency)
        ball_distribution = ball_tmp / np.sum(ball_tmp)

        single_tmp = self._calculate_raw_distribution(single_frequency)
        single_distribution = single_tmp / np.sum(single_tmp)

        return ball_distribution, single_distribution

    def train(self, ball_draws, single_draws):
        """ """
        self.ball_distribution, self.single_distribution = (
            self._calculate_normalized_distribution(ball_draws, single_draws)
        )

    def predict(self):
        """ """
        top_balls = (np.argsort(self.ball_distribution) + 1)[-5:]
        top_single = (np.argsort(self.single_distribution) + 1)[-1]
        return top_balls, top_single


class PowerballAnalyzer(Analyzer):
    DB_ADDRESS = "sqlite:///Powerball.db"
    BALL_RANGE = np.arange(1, 70)
    SINGLE_RANGE = np.arange(1, 27)
    CLEANER = PowerballCleaner2015


class MegaMillionsAnalyzer(Analyzer):
    DB_ADDRESS = "sqlite:///MegaMillions.db"
    BALL_RANGE = np.arange(1, 71)
    SINGLE_RANGE = np.arange(1, 26)
    CLEANER = MegaMillionsCleaner2017
