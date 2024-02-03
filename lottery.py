#!/usr/bin/env python3
import inquirer

from scraper import PowerballScraper, MegaMillionsScraper
from analyzer import PowerballAnalyzer, MegaMillionsAnalyzer


if __name__ == "__main__":
    function = inquirer.prompt(
        [
            inquirer.List(
                "purpose",
                "What would you like to do?",
                choices=["Update Database", "Retrain RNN", "Update RNN", "Predict"],
            )
        ]
    )

    if function["purpose"] == "Update Database":
        PowerballScraper.scrape_and_store()
        MegaMillionsScraper.scrape_and_store()
    elif function["purpose"] == "Predict":
        predict = inquirer.prompt(
            [
                inquirer.List(
                    "predict",
                    "What prediction method would you like to use?",
                    choices=["RNN", "Probabalistic"],
                )
            ]
        )

    if predict["predict"] == "RNN":
        pass
    elif predict["predict"] == "Probabalistic":
        PowerballAnalyzer()
