import sqlalchemy as db
import numpy as np

from sqlalchemy.orm import Session
from models import WinningNumbers

class Analyzer:
    # [,)
    ball_range = np.arange(1, 70)
    powerball_range =  np.arange(1, 27)

    def __init__(self):
        self.engine = db.create_engine('sqlite:///Powerball.db')
        stored_numbers = self._read_all_winning_numbers()
        print(self._get_least_occurring_ball(stored_numbers))
        print(self._get_least_occurring_powerball(stored_numbers))

    def _read_all_winning_numbers(self):
        with Session(bind=self.engine) as sess:
            query = sess.query(WinningNumbers.numbers).all()
            stored_numbers = [numbers[0].strip('[]').split(', ') for numbers in query]

        return np.array(stored_numbers, dtype=int)

    def _get_least_occurring_ball(self, stored_numbers):
        ball_numbers = stored_numbers.T[:-1]

        min_numbers = []
        for row in ball_numbers:
            missing = self._check_for_missing(self.ball_range, row)

            if any(missing):
                min_numbers.append(missing)
                continue
            
            min_numbers.append(self._get_min_occurrence(row))

        return min_numbers

    def _get_least_occurring_powerball(self, stored_numbers):
        powerball_numbers = stored_numbers.T[-1]
        clean_powerball = self._clean_powerball(powerball_numbers)
        missing = self._check_for_missing(self.powerball_range, clean_powerball)

        if any(missing):
            return missing

        return self._get_min_occurrence(clean_powerball)

    def _clean_powerball(self, powerball_numbers):
        mask = powerball_numbers <= 26
        return powerball_numbers[mask]

    def _check_for_missing(self, numbers, truth):
            missing = np.where(np.isin(truth, numbers, invert=True))
            return missing[0]

    def _get_min_occurrence(self, numbers):
            # index of lowest occurrence
            # indices are 0 to 68
            # this currently only return one value if even multiple are equal in occurence
            arg_occ = np.unique(numbers, return_counts=True)
            min_index = np.argmin(arg_occ[1])
            return arg_occ[0][min_index] + 1


if __name__ == "__main__":
    Analyzer()
