import sqlalchemy as db
import numpy as np

from sqlalchemy.orm import Session
from pandas import DataFrame, to_datetime
from models import WinningNumbers
from cleaner import PowerballCleaner2015

class Analyzer:
    # [,)
    ball_range = np.arange(1, 70)
    powerball_range =  np.arange(1, 27)

    def __init__(self):
        self.engine = db.create_engine('sqlite:///Powerball.db')
        winning_numbers = self._read_all_winning_numbers()
        powerball_cleaner = PowerballCleaner2015(winning_numbers)

        print(self._get_least_occurring_ball(powerball_cleaner.ball_numbers))
        print(self._get_least_occurring_powerball(powerball_cleaner.powerball_numbers))

    def _read_all_winning_numbers(self):
        with Session(bind=self.engine) as sess:
            query = sess.query(WinningNumbers.date, WinningNumbers.numbers).all()
            dates = to_datetime([result[0] for result in query])
            stored_numbers = [result[1].strip('[]').split(', ') for result in query]

        return DataFrame(data=stored_numbers, index=dates).astype(int)

    def _get_least_occurring_ball(self, ball_numbers):
        missing = self._check_for_missing(self.ball_range, ball_numbers)
        normalized_numbers = np.append(ball_numbers, missing)

        elements, frequency = np.unique(normalized_numbers, return_counts=True)
        return elements[np.argsort(frequency)[:5]]

    def _get_least_occurring_powerball(self, powerball_numbers):
        missing = self._check_for_missing(self.powerball_range, powerball_numbers)
        normalized_numbers = np.append(powerball_numbers, missing)

        elements, frequency = np.unique(normalized_numbers, return_counts=True)
        return elements[np.argsort(frequency)[0]]

    def _check_for_missing(self, numbers, truth):
            missing = np.where(np.isin(truth, numbers, invert=True))
            return missing[0]


if __name__ == "__main__":
    Analyzer()
