import requests
import sqlalchemy as db
from collections import namedtuple

from datetime import datetime as dt
from sqlalchemy.orm import Session
from models import LotteryDraw


WinningNumbers = namedtuple("WinningNumber", "date numbers single")


class FivePlusOneScraper:
    """
    Downloads and ingests lottery data from games of format 'N N N N N P'
    """

    DATE_SLICE = slice(1, 4)
    NUMBERS_SLICE = slice(4, 9)
    SINGLE_INDEX = 9

    @classmethod
    def _get_latest_data(cls):
        response = requests.get(cls.download_url)

        if response.status_code == 200:
            csv_data = response.text
        # potential to fail here without exception

        numbers_data = []

        for row in [csv_row for csv_row in csv_data.split("\n") if csv_row]:
            row_list = row.split(",")
            # sqlite only supports - formatting for dates
            current_date = dt.strptime(
                "-".join(row_list[cls.DATE_SLICE]), "%m-%d-%Y"
            ).date()

            # sqlite doesn't support arrays, so we store as a string
            winning_numbers = str(
                [int(number) for number in row_list[cls.NUMBERS_SLICE]]
            )
            single = row_list[cls.SINGLE_INDEX]
            numbers_data.append(WinningNumbers(current_date, winning_numbers, single))

        return numbers_data

    @staticmethod
    def _store_winning_numbers(numbers_data, engine):
        winning_numbers = [
            LotteryDraw(date=item.date, numbers=item.numbers, single=item.single)
            for item in numbers_data
        ]

        with Session(bind=engine) as sess:
            sess.add_all(winning_numbers)
            sess.commit()

    @staticmethod
    def _filter_new_numbers(numbers_data, engine):
        with Session(bind=engine) as sess:
            query = sess.query(LotteryDraw.date).distinct()
            stored_dates = [row[0] for row in query]

        return [
            WinningNumbers(winner.date, winner.numbers, winner.single)
            for winner in numbers_data
            if winner.date not in stored_dates
        ]

    @classmethod
    def scrape_and_store(cls):
        engine = db.create_engine(cls.db_address)

        numbers_data = cls._get_latest_data()
        filtered_data = cls._filter_new_numbers(numbers_data, engine)

        cls._store_winning_numbers(filtered_data, engine)


class PowerballScraper(FivePlusOneScraper):
    download_url = "https://www.texaslottery.com/export/sites/lottery/Games/Powerball/Winning_Numbers/powerball.csv"
    db_address = "sqlite:///Powerball.db"


class MegaMillionsScraper(FivePlusOneScraper):
    download_url = "https://www.texaslottery.com/export/sites/lottery/Games/Mega_Millions/Winning_Numbers/megamillions.csv"
    db_address = "sqlite:///MegaMillions.db"


if __name__ == "__main__":
    PowerballScraper()
    MegaMillionsScraper()
