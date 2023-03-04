import sqlalchemy as db
import numpy as np

from sqlalchemy.orm import Session
from pandas import DataFrame, to_datetime
from models import WinningNumbers
from cleaner import PowerballCleaner2015

class Analyzer:
    # [,)
    # TODO: work in numbers with equal occurrences
    ball_range = np.arange(1, 70)
    powerball_range =  np.arange(1, 27)

    def __init__(self):
        self.engine = db.create_engine('sqlite:///Powerball.db')
        self.winning_numbers = self._read_all_winning_numbers()
        self.powerball_cleaner = PowerballCleaner2015(self.winning_numbers)

        #self._calculate_distribution(self.winning_numbers)

        print(self._get_least_occurring_ball(self.powerball_cleaner.ball_numbers))
        print(self._get_least_occurring_powerball(self.powerball_cleaner.powerball_numbers))

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
        return np.sort(elements[np.argsort(frequency)[:5]])

    def _get_least_occurring_powerball(self, powerball_numbers):
        missing = self._check_for_missing(self.powerball_range, powerball_numbers)
        normalized_numbers = np.append(powerball_numbers, missing)

        elements, frequency = np.unique(normalized_numbers, return_counts=True)
        return elements[np.argsort(frequency)[0]]

    def _check_for_missing(self, numbers, truth):
            missing = np.where(np.isin(truth, numbers, invert=True))
            return missing[0]

    def _calculate_distribution(self, dataframe, draw_date):
        """
        Returns normalized draw distribution
        """
        ball_draws, powerball_draws = self.powerball_cleaner.get_ball_and_powerball_arrays(dataframe)
        ball_frequency = self._get_occurrences(ball_draws)
        powerball_frequency = self._get_occurrences(powerball_draws)

        # TODO: this bit is in dire need of unit testing due to int wrapping
        ball_tmp = 1 / np.power(ball_frequency.size, (ball_frequency + 1), dtype=np.double)
        ball_distribution = ball_tmp/np.sum(ball_tmp)

        powerball_tmp = 1 / np.power(powerball_frequency.size, (powerball_frequency + 1), dtype=np.double)
        powerball_distribution = powerball_tmp/np.sum(powerball_tmp)

        return ball_distribution, powerball_distribution
    
    def _get_occurrences(self, ball_draws):
        """
        Returns frequency with 0 for draws that have not occurred
        """
        ball_array, ball_frequency = np.unique(ball_draws, return_counts=True)

        missing_ball_indicies = np.where(np.isin(self.ball_range, ball_array, invert=True))
        missing_ball_indicies -= np.arange(missing_ball_indicies.size)

        # TODO: unit test the proper filling of 0s
        return np.insert(ball_frequency, missing_ball_indicies, 0)


if __name__ == "__main__":
    Analyzer()
