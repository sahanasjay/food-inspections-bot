# Food Inspections in College Park

## Overview
The code in this repo builds and executes a Slack bot that pulls food inspection data from a csv published by Prince George's county and updated once a week. Each time the bot runs, a little [shell script](https://github.com/sahanasjay/food-inspections-bot/blob/main/app.sh) pulls down the latest version of the csv. Then, a python script — labeled [app.py](https://github.com/sahanasjay/food-inspections-bot/blob/main/app.py) — parses the data and cleans it, filtering for new records of establishments in College Park and adding them to a sqlite database named [food_inspections.db](https://github.com/sahanasjay/food-inspections-bot/blob/main/food_inspections.db).  

The bot goes into that db it just added to and retrieves all recent inspections that have an inspection_result of 'Critical Violations Observed" or "non-Compliant - Violations Observed.' If there are new rows (which are defined here as "rows with a date stamp later than the max date last retrieved from the database") the bot uses some for loops, functions and dictionary-wrangling to send the channel:  

1. A main message that contains summary information: The number of inspections that resulted in a violation in College Park in the past week, and the names of impacted establishments.  
2. Threaded messages that give users details on each impacted establishment, like the date of the most recent inspection and what triggered it; the number of inspections a business had before and how many of them resulted in a violation; business location (address); the reasons a business failed the inspection; and links to the data and the county's MPIA form, in case reporters want to dig in more.

If there are no new records added to the database, the app still sends a message — it just tells the channel to check back in next week.
