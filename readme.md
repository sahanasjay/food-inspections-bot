#Food Inspections in College Park

##Overview
The code in this repo builds and executes a Slack bot that pulls food inspection data from a csv published by Prince George's county snd updated once a week. Each time the bot runs, a shell script pulls down the latest version of the csv. Then, a python script — labeled app.py — parses the data and cleans it, filtering for new records of establishments in College Park and adding them to a sqlite database named food_inspections.db.  

The bot goes into that db it just added to and retrieves all recent inspections that have an inspection_result of 'Critical Violations Observed" or "non-Compliant - Violations Observed.' If there are new rows (which are defined here as "rows with a date stamp later than the max date last retrieved from the database") the bot uses some for loops, functions and dictionary wrangling to send the channel:  

a) a main message that contains summary information: The number of inspections that resulted in a violation in College Park in the past week, and the names of impacted   the bot retrieves the data to establishments only in College Park and pulls it into a database. Later, we might consider making this data queryable, maybe even as part of a direct chat between a user and the bot in Slack.

2. If this bot were able to accept input from users, what would that look like and how might it respond?

Looking ahead, we’ve considered allowing users in Slack to communicate directly with the bot. After receiving a scheduled food inspection update at an establishment in College Park, the user might then ask the bot for a history of inspections at a given establishment. The user might also ask when the last inspection was or if there are any inspections on record at all. A user might also ask questions about a specific violation, such as,  “Is [type of violation] common in College Park?” This query could yield all College Park records of a given violation.

3. What's the best schedule for updates?

This API is updated fairly frequently, but it does not appear to be updated in real-time. While we cannot confirm this, the API has released updates on a weekly basis. Since we’re still nailing down the specifics of the API’s own schedule and we want to recognize that this schedule could change, we plan to scrape for inspections daily at 8 a.m. Often, this will likely return no new results if the API is indeed updated weekly, but if there is a stray submission, we want to be on top of it.

4. A note about where we are with the bot:

Working on making sure the bot only pulls most recent info from JSON API (almost there!), then must update the git actions yml file to make it run smoothly. Next step after that: making the bot responsive.
