#!/usr/bin/env python3
import inquirer
import pickle

from scraper import PowerballScraper, MegaMillionsScraper
from analyzer import PowerballAnalyzer, MegaMillionsAnalyzer, ProbabalisticModel
from cleaner import PowerballCleaner2015


if __name__ == "__main__":
    function = inquirer.prompt(
        [
            inquirer.List(
                "purpose",
                "What would you like to do?",
                choices=["Update the databse", "Train a model", "Make a prediction"],
            )
        ]
    )

    if function["purpose"] == "Update the database":
        PowerballScraper.scrape_and_store()
        MegaMillionsScraper.scrape_and_store()
    elif function["purpose"] == "Train a model":
        model = inquirer.prompt(
            [
                inquirer.List(
                    "model",
                    "What type of model would you like to train?",
                    choices=["RNN", "Probabalistic"],
                )
            ]
        )
        if model["model"] == "Probabalistic":
            game = inquirer.prompt(
                [
                    inquirer.List(
                        "game",
                        "What game would you like to train the model on?",
                        choices=["Powerball"],
                    )
                ]
            )
            if game["game"] == "Powerball":
                analyzer = PowerballAnalyzer(
                    cleaner=PowerballCleaner2015, model=ProbabalisticModel
                )
                analyzer.save("models/ppba.pkl")
        elif model["model"] == "RNN":
            pass
    elif function["purpose"] == "Make a prediction":
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
            analyzer = PowerballAnalyzer.load("models/ppba.pkl")
            print(analyzer.predict())
