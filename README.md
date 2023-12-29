# What is this?
A CLI application that returns most likely next draw for lottery numbers. Currently, it only supports PowerBall, and uses a probablistic determination assuming that the underlying distirbution is uniform.

# Getting Started
## Requirements
- python3
- pipenv
- sqlite3

```
# Build the venv
~/Powerball$: pipenv install --deploy

# Update the database(s)
~/Powerball$: ./scraper.py

# Run it!
~/Powerball$: ./analyzer.py
```

# Future Work
- Unit testing for:
    - Correct historical data
    - Cleaning
    - Probability calculation
    - Float wrapping
- Support for MegaMillions
- Explore more sophisticated perdictive methods based on known data
