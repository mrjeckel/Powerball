
import requests
import sqlalchemy as db

from collections import namedtuple
from datetime import datetime as dt
from sqlalchemy.orm import Session
from models import WinningNumbers

class Scraper:
    WinningNumbers = namedtuple("WinningNumber", "date numbers")

    def __init__(self):
        self.engine = db.create_engine(self.db_address)

        powerball_data = self._get_latest_data()
        filtered_data = self._filter_new_numbers(powerball_data)

        self._store_winning_numbers(filtered_data)

    def _get_latest_data(self):
        response = requests.get(self.download_url)

        if response.status_code == 200:
            csv_data = response.text
        # potential to fail here without exception

        powerball_data = []

        for row in [csv_row for csv_row in csv_data.split('\n') if csv_row]:
            row_list = row.split(',')
            # sqlite only supports - formatting for dates
            current_date = dt.strptime('-'.join(row_list[1:4]), '%m-%d-%Y').date()

            # sqlite doesn't support arrays, so we store as a string
            winning_numbers = str([int(number) for number in row_list[4:10]])
            powerball_data.append(self.WinningNumbers(current_date, winning_numbers))

        return powerball_data

    def _store_winning_numbers(self, powerball_data):
        winning_numbers = [WinningNumbers(date=item.date, numbers=item.numbers)
            for item in powerball_data]

        with Session(bind=self.engine) as sess:
            sess.add_all(winning_numbers)
            sess.commit()

    def _filter_new_numbers(self, powerball_data):
        with Session(bind=self.engine) as sess:
            query = sess.query(WinningNumbers.date).distinct()
            stored_dates = [date[0] for date in query]

        return [self.WinningNumbers(winner.date, winner.numbers)
            for winner in powerball_data if winner.date not in stored_dates]
    

class PowerballScraper(Scraper):
    download_url = 'https://www.texaslottery.com/export/sites/lottery/Games/Powerball/Winning_Numbers/powerball.csv'
    db_address = 'sqlite:///Powerball.db'


class MegaMillionsScraper(Scraper):
    download_url = 'https://www.texaslottery.com/export/sites/lottery/Games/Mega_Millions/Winning_Numbers/megamillions.csv'
    db_address = 'sqlite:///MegaMillions.db'


if __name__ == "__main__":
    PowerballScraper()
    MegaMillionsScraper()
