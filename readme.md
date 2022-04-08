Food Inspections in College Park

1. Do I need to store this data somehow? What would that look like?

This bot scrapes data from an API that stores Prince George’s County food inspections records. The bot filters the data to establishments only in College Park and pulls it into a database. Later, we might consider making this data queryable, maybe even as part of a direct chat between a user and the bot in Slack.

2. If this bot were able to accept input from users, what would that look like and how might it respond?

Looking ahead, we’ve considered allowing users in Slack to communicate directly with the bot. After receiving a scheduled food inspection update at an establishment in College Park, the user might then ask the bot for a history of inspections at a given establishment. The user might also ask when the last inspection was or if there are any inspections on record at all. A user might also ask questions about a specific violation, such as,  “Is [type of violation] common in College Park?” This query could yield all College Park records of a given violation.

3. What's the best schedule for updates?

This API is updated fairly frequently, but it does not appear to be updated in real-time. While we cannot confirm this, the API has released updates on a weekly basis. Since we’re still nailing down the specifics of the API’s own schedule and we want to recognize that this schedule could change, we plan to scrape for inspections daily at 8 a.m. Often, this will likely return no new results if the API is indeed updated weekly, but if there is a stray submission, we want to be on top of it.
