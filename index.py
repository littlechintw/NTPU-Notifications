import urllib
import json
import os
import random
import sys
from bs4 import BeautifulSoup
import re
from urllib.parse import unquote as decode

from flask import Flask
from flask import request
from flask import make_response
import time,datetime
import requests
import feedparser

# Flask app should start in global layout
app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("queryResult").get("intent").get("displayName") == "new massege":
        logs_yellow("goto new_massege")
        n = int(req.get("queryResult").get("parameters").get("number"))
        if (n<1 or n>10):
            speech = "我只找的到最新 10 則的訊息噢！"
        else: 
            mess = str(get_new_mess_data(n))
            if mess == 'no':
                speech = '很抱歉，目前系統發生錯誤，請稍後再試。'
            else:
                speech = "第 " + str(n) + " 則訊息是: " + mess
        print("Response:")
        print(speech)
        return {
            "fulfillmentText": speech,
        }
    elif req.get("queryResult").get("intent").get("displayName") == "first new mess":
        logs_yellow("goto first_new_mess")
        mess = str(get_new_mess_data(1))
        if mess == 'no':
            speech = '很抱歉，目前系統發生錯誤，請稍後再試。'
        else:
            speech = "第 1 則訊息是: " + mess
        print("Response:")
        print(speech)
        return {
            "fulfillmentText": speech,
        }
    elif req.get("queryResult").get("intent").get("displayName") == "new events":
        logs_yellow("goto new_events")
        n = int(req.get("queryResult").get("parameters").get("number"))
        if (n<1 or n>10):
            speech = "我只找的到最新 10 則的活動噢！"
        else: 
            mess = str(get_new_events_data(n))
            if mess == 'no':
                speech = '很抱歉，目前系統發生錯誤，請稍後再試。'
            else:
                speech = "第 " + str(n) + " 個活動是" + mess
        print("Response:")
        print(speech)
        return {
            "fulfillmentText": speech,
        }
    elif req.get("queryResult").get("intent").get("displayName") == "first new events":
        logs_yellow("goto first_new_events")
        mess = str(get_new_events_data(1))
        if mess == 'no':
            speech = '很抱歉，目前系統發生錯誤，請稍後再試。'
        else:
            speech = "第 1 個活動是" + mess
        print("Response:")
        print(speech)
        return {
            "fulfillmentText": speech,
        }
    logs_yellow("nothing")
    return {}

def get_new_mess_data(n):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://new.ntpu.edu.tw/news",
        "Origin": "https://new.ntpu.edu.tw",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "DNT": "1",
        "Sec-Fetch-Mode": "cors",
        "Content-type": "application/json; charset=UTF-8"
    }
    now_time = str(time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.localtime()))
    data_data  = "\n{\npublications(\nstart: 0,\nlimit: 10,\nsort: \"publishAt:desc,createdAt:desc\",\nwhere: {\nsitesApproved: \"www_ntpu\",\npublishAt_lte: \""
    data_data += now_time
    data_data += "\",\nunPublishAt_gte: \""
    data_data += now_time
    data_data += "\"\n}\n)\n{_id title tags contactPerson publishAt coverImage{url}}\n}"
    data = json.dumps({"query":data_data})
    
    try:
        r = requests.post("https://cms.carrier.ntpu.edu.tw/graphql", headers=headers, data=data)
        r.encoding = 'utf8'
        soup = BeautifulSoup(r.text, 'html.parser')
        logs_yellow('Get data!')
    except:
        logs_yellow('[Get data!] Fail')
        return 'no'
    else:
        logs_yellow('[Get data!] Success')
        # print(str(soup))
        json_dict = json.loads(str(soup))
        json_data = json_dict['data']['publications']
        return (str(json_data[n-1]['title']) + '\n您也可以說「第二則通知」或是「再會」離開對話。')

def get_new_events_data(n):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://new.ntpu.edu.tw/events",
        "Origin": "https://new.ntpu.edu.tw",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "DNT": "1",
        "Content-type": "application/json; charset=UTF-8"
    }
    data_data = "{\npublications(\nsort:\"eventStartAt:asc,createdAt:desc\"\nlimit: 100\nwhere: { isEvent: true, sitesApproved_contains: \"www_ntpu\" }\n  ) {_id title eventStartAt eventLocation eventOpenTo }\n}"
    data = json.dumps({"query":data_data})
    
    try:
        r = requests.post("https://cms.carrier.ntpu.edu.tw/graphql", headers=headers, data=data)
        r.encoding = 'utf8'
        soup = BeautifulSoup(r.text, 'html.parser')
        logs_yellow('Get data!')
    except:
        logs_yellow('[Get data!] Fail')
        return 'no'
    else:
        logs_yellow('[Get data!] Success')
        json_dict = json.loads(str(soup))
        json_data = json_dict['data']['publications']
        time  = json_data[n-1]['eventStartAt'][0:4] + '年'
        time += json_data[n-1]['eventStartAt'][5:7] + '月'
        time += json_data[n-1]['eventStartAt'][8:10] + '日'
        return ('在 ' + time + ' 有「' + str(json_data[n-1]['title']) + '」的活動' + '\n順道一提，您也可以說「第二個活動」或是「再會」離開對話。')

def get_nowtime():
    return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

def logs_yellow(mess):
    print('\033[33m [' + get_nowtime() + '] ' + mess + ' \033[0m')
    return "success"

def logs_green(mess):
    print('\033[32m [' + get_nowtime() + '] ' + mess + ' \033[0m')
    return "success"

if __name__ == "__main__":
    app.run(debug=True,port=80)
