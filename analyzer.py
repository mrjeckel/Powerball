import pickle
from typing import Union

import numpy as np
import pandas as pd
from pandas import DataFrame, to_datetime
import sqlalchemy as db
from sqlalchemy.orm import Session

from models import LotteryDraw
from cleaner import PowerballCleaner2015, MegaMillionsCleaner2017


class Analyzer:
    def __init__(self, cleaner, model):
        """ """

        self.last_draw = None
        self.cleaner = cleaner()
        self.model = model()

        winning_numbers = self._read_winning_numbers()
        self.last_draw = winning_numbers.index[-1]

        ball_draws, single_draws = self.cleaner.get_ball_and_powerball_arrays(
            winning_numbers
        )
        self.model.train(ball_draws, single_draws)
        self.graph_performance(ball_draws)

    def _read_winning_numbers(self, partial=False) -> pd.DataFrame:
        """
        Read winning numbers from the database

        Parameters:
            partial[bool]: if True, only return draws after self.last_draw
        """

        with Session(bind=db.create_engine(self.DB_ADDRESS)) as sess:
            if self.last_draw and partial:
                query = sess.query(
                    LotteryDraw.date, LotteryDraw.numbers, LotteryDraw.single
                ).filter(LotteryDraw.date > self.last_draw)
            else:
                query = sess.query(
                    LotteryDraw.date, LotteryDraw.numbers, LotteryDraw.single
                )
            draws = query.order_by(LotteryDraw.date.asc()).all()

        dates = to_datetime([draw[0] for draw in draws])
        stored_numbers = [(*draw[1].strip("[]").split(", "), draw[2]) for draw in draws]
        return DataFrame(data=stored_numbers, index=dates).astype(int)

    def update(self):
        """ """
        winning_numbers = self._read_winning_numbers(partial=True)
        ball_draws, single_draws = self.cleaner.get_ball_and_powerball_arrays(
            winning_numbers
        )
        self.model.update(ball_draws, single_draws)

    def predict(self):
        """ """
        top_balls, top_single = self.model.predict()
        return f"{top_balls} : {top_single}"

    def save(self, path):
        """
        Pickle the model
        """
        with open(path, "wb") as fd:
            pickle.dump(self, fd)

    def graph_performance(self, draws):
        """ """
        # TODO: Clean data so that we don't have a probability of drawing a non-existant ball
        predictions = self.model.ball_distribution.agg(
            lambda x: (x.argsort() + 1)[-5:], axis=1
        )
        # TODO: Find count in draws where predictions is 1 -> new Series
        # TODO: Do the same for single and add them together
        # TODO: Convert to a ratio of correct/total
        # TODO: Plot a rolling average of correct %
        import pdb

        pdb.set_trace()

    @staticmethod
    def load(path):
        """
        Load a pickled model
        """
        with open(path, "rb") as fd:
            return pickle.load(fd)


class ProbabalisticModel:
    """ """

    def _fill_cleaned_data(self, distribution: pd.Series, draws: pd.DataFrame, index: int) -> np.ndarray:
        """
        Fill the distrubtion when numbers are added or removed from play
        """
        distribution = distribution.mask((np.isnan(draws.iloc[index - 1]) & ~np.isnan(draws.iloc[index])), distribution.median())
        distribution = distribution.mask((~np.isnan(draws.iloc[index - 1]) & np.isnan(draws.iloc[index])), distribution.median())
        return distribution

    def _calculate_normalized_distribution(
        self, draws: Union[pd.DataFrame, pd.Series]
    ) -> pd.DataFrame:
        """
        Returns a normalized probability distribution for each draw
         Probability is first calculated by V = 1 / Size^B
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
            dtype=np.longdouble,
        )

        for date, index in zip(draws.iloc[1:].index, range(1, draws.size)):
            distribution.loc[date] = np.multiply(
                1 / np.power(width, draws.iloc[index - 1]),
                distribution.iloc[index - 1],
            )

            distribution.loc[date] = self._fill_cleaned_data(distribution.loc[date], draws, index)
            distribution.loc[date] = distribution.loc[date] / np.sum(
                distribution.loc[date]
            )

        current_distribution = np.multiply(
            1 / np.power(width, draws.iloc[-1]), distribution.iloc[-1]
        )
        current_distribution = current_distribution / np.sum(current_distribution)

        return distribution, current_distribution

    def update(self):
        """ """
        pass

    def train(self, ball_draws, single_draws):
        """
        Calculate the probability ball and single draws
        """
        self.ball_distribution, self.current_ball_distribution = (
            self._calculate_normalized_distribution(ball_draws)
        )
        self.single_distribution, self.current_single_distribution = (
            self._calculate_normalized_distribution(single_draws)
        )

    def predict(self):
        """
        Take the highest probability draws from both current distributions
        """
        import pdb

        pdb.set_trace()
        top_balls = (np.argsort(self.current_ball_distribution.fillna(0)) + 1)[-5:]
        top_single = (np.argsort(self.current_single_distribution.fillna(0)) + 1)[-1:]
        return sorted(top_balls.values), top_single.values


class PowerballAnalyzer(Analyzer):
    DB_ADDRESS = "sqlite:///Powerball.db"
    BALL_RANGE = np.arange(1, 70)
    CLEANER = PowerballCleaner2015


class MegaMillionsAnalyzer(Analyzer):
    DB_ADDRESS = "sqlite:///MegaMillions.db"
    BALL_RANGE = np.arange(1, 71)
    BALL_COLUMNS = np.arange(0, 5)
    SINGLE_RANGE = np.arange(1, 26)
    SINGLE_INDEX = 5
    CLEANER = MegaMillionsCleaner2017
