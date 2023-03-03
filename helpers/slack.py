import time
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import SLACK_API_TOKEN

client = WebClient(token=SLACK_API_TOKEN)

def postMessage(channel, message):
    try:
        response = client.chat_postMessage(channel=channel,text=message)
        return response["ts"]
    except SlackApiError as e:
        print("SlackApiError: {}".format(e))
    except Exception as e:
        print("UnknownError: {}".format(e))
    return None

def chatUpdate(channel, message, ts):
    try:
        return client.chat_update(channel=channel,text=message,ts=ts)
    except SlackApiError as e:
        print("SlackApiError: {}".format(e))
    except Exception as e:
        print("UnknownError: {}".format(e))
    return None