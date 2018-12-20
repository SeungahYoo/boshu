# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
import ast
from crawl import _crawl_naver_keywords

from slacker import Slacker

import requests

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template, jsonify

app = Flask(__name__)

slack_token = 'xoxb-503818135714-506852761857-V1xcxpKanO7YOWXSZYFIhsd2'
slack_client_id = '503818135714.507348866547'
slack_client_secret = '1fb4309701edc44269c681c494bed569'
slack_verification = 'cupsHgeL0hFVq3B6kz3IWAbY'
sc = SlackClient(slack_token)
slack = Slacker(slack_token)

# boshu와 대화를 하는 user
user_list = {}

#dialogFlow 에 text 를 넣고 그것에 대한 대답을 dictionary타입으로 받는다.
def get_answer(text, user_key):
    data_send = {
        'query': text,
        'sessionId': user_key,
        'lang': 'ko',
    }

    data_header = {
        'Authorization': 'Bearer 7af062e799994609aea8846103f61084',
        'Content-Type': 'application/json; charset=utf-8'
    }

    dialogflow_url = 'https://api.dialogflow.com/v1/query?v=20150910'
    res = requests.post(dialogflow_url, data=json.dumps(data_send), headers=data_header)

    if res.status_code != requests.codes.ok:
        return '오류가 발생했습니다.'

    data_receive = res.json()
    result = {
        "speech" : data_receive['result']['fulfillment']['speech'],
        "intent" : data_receive['result']['metadata']['intentName']
    }
    return result

def make_query(text):
    result = ''
    for i in text:
        result += i
        result += ' '
    return result

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]
        userid = slack_event["event"]["user"]

        if text.find("reset") != -1:
            user_list[userid] = []
            feedback = '드라마, 예능, 시사 중 선택해주세요.'
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=feedback
            )
            return make_response("App mention message has been sent", 200, )

        if userid not in user_list:
            print("되고이따11")
            user_list[userid] = []
            feedback = '드라마, 예능, 시사 중 선택해주세요.'

        else:
            print("여기이따22")
            dialog_answer = get_answer(text, userid)
            print(dialog_answer)
            answer = dialog_answer['speech'].split()[1]
            if len(user_list[userid]) == 0:
                if answer not in ['드라마', '예능', '시사']:
                    user_list[userid] = []
                    feedback = '드라마, 예능, 시사 중 선택해주세요.'
                    sc.api_call(
                        "chat.postMessage",
                        channel=channel,
                        text=feedback
                    )
                    return make_response("App mention message has been sent", 200, )
                user_list[userid].append(answer)
                feedback = '제목을 입력해주세요.'
            elif len(user_list[userid]) == 1:
                user_list[userid].append(answer)
                feedback = _crawl_naver_keywords(make_query(user_list[userid]))
                del user_list[userid]
                print(feedback)
                slack.files.upload(content=feedback[0])
                print(feedback[0])
                for i in range(1, len(feedback)):
                    slack.chat.post_message(channel=channel, text=feedback[i])
                return make_response("App mention message has been sent", 200, )
            print(answer)

        #keywords = _crawl_naver_keywords(answer)

        # slack.chat.post_message(channel=channel, text=feedback)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=feedback
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})



@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})





@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=8000)
