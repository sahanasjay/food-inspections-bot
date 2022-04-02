import os
from slack import WebClient
from slack.errors import SlackApiError

client = WebClient()

slack_token = os.environ["SLACK_API_TOKEN"]
client = WebClient(token=slack_token)

try:
  response = client.chat_postMessage(
    channel="slack-bots",
    text="You look good today :)"
  )
except SlackApiError as e:
  # You will get a SlackApiError if "ok" is False
  assert e.response["error"]
