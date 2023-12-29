# Getting Started
You'll need python3, pipenv, and sqlite.

```
# Install sqlite
~/Powerball$: sudo apt install sqlite3

# Install pipenv
~/Powerball$: sudo pip install pipenv

# Build the venv
~/Powerball$: pipenv install --deploy

# Update the database(s)
~/Powerball$: ./scraper.py

# Run it!
~/Powerball$: ./analyzer.py
```

# To-Do
- Unit testing for:
    - Correct historical data
    - Cleaning
    - Probability calculation
    - Float wrapping
- Support for MegaMillions
- Explore more sophisticated perdictive methods based on known data
