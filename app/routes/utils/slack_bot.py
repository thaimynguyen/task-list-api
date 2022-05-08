import requests
import time
import json
import os


def send_notification(text):

    url = "https://slack.com/api/chat.postMessage"

    SLACK_API_KEY = os.environ.get("SLACK_API_KEY")

    payload = {
        "channel": "task-notifications",
        "text": text}

    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {SLACK_API_KEY}"}

    # to avoid API rate limit
    retry_count = 0
    max_retries = 5
    wait_time = 2

    while retry_count <= max_retries:
        response = requests.post(
            url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            time.sleep(wait_time)
            retry_count += 1
            wait_time *= 2
        else:
            break

    return response
