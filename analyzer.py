import sqlalchemy as db
import numpy as np
from typing import Union

from sqlalchemy.orm import Session
import pandas as pd
from pandas import DataFrame, to_datetime
from models import LotteryDraw
from cleaner import PowerballCleaner2015, MegaMillionsCleaner2017


class Analyzer:
    def __init__(self, model):
        self.engine = db.create_engine(self.DB_ADDRESS)
        winning_numbers = self._read_all_winning_numbers()
        self.ball_draws, self.single_draws = self.CLEANER.get_ball_and_powerball_arrays(
            winning_numbers, self.BALL_COLUMNS, self.SINGLE_INDEX
        )

        self.model = model()
        self.train()

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

    def _calculate_normalized_distribution(
        self, draws: Union[pd.DataFrame, pd.Series]
    ) -> pd.DataFrame:
        """
        Returns a normalized probability distribution
         Probability is first calculated by V = 1 / Size^N
          Then normalized by V / V.Sum
        """
        if isinstance(draws, pd.Series):
            width = 1
        else:
            width = draws.shape[1]

        distribution = pd.DataFrame(
            [[1 / width] * width],
            columns=np.arange(1, width + 1),
            index=draws.index,
        )

        for date, index in zip(draws.iloc[1:].index, range(1, draws.size)):
            distribution.loc[date] = np.multiply(
                1 / np.power(draws.size, draws.iloc[index - 1]),
                distribution.iloc[index - 1],
            )
            distribution.loc[date] = distribution.loc[date] / np.sum(
                distribution.loc[date]
            )
        import pdb

        pdb.set_trace()
        return distribution

    def train(self, ball_draws, single_draws):
        """ """
        self.ball_distribution = self._calculate_normalized_distribution(ball_draws)
        self.single_distribution = self._calculate_normalized_distribution(single_draws)

    def predict(self):
        """ """
        top_balls = (np.argsort(self.ball_distribution) + 1)[-5:]
        top_single = (np.argsort(self.single_distribution) + 1)[-1]
        return top_balls, top_single


class PowerballAnalyzer(Analyzer):
    DB_ADDRESS = "sqlite:///Powerball.db"
    BALL_RANGE = np.arange(1, 70)
    BALL_COLUMNS = np.arange(0, 5)
    SINGLE_RANGE = np.arange(1, 27)
    SINGLE_INDEX = 5
    CLEANER = PowerballCleaner2015


class MegaMillionsAnalyzer(Analyzer):
    DB_ADDRESS = "sqlite:///MegaMillions.db"
    BALL_RANGE = np.arange(1, 71)
    BALL_COLUMNS = np.arange(0, 5)
    SINGLE_RANGE = np.arange(1, 26)
    SINGLE_INDEX = 5
    CLEANER = MegaMillionsCleaner2017


PowerballAnalyzer(ProbabalisticModel)
