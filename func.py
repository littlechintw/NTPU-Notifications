import requests
import time
import sqlite3
import json

def getItem():
    now_time = str(time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.localtime()))
    post_data = {
        "query": "{\npublications(\nsort: \"publishAt:desc,createdAt:desc\"\nstart: 0\nlimit: 20\nwhere: {\n  isEvent: false\n  sitesApproved_contains: \"www_ntpu\"\n  \n  lang_ne: \"english\"\n  tags_contains: [[]]\n  \n  publishAt_lte: \"" + now_time + "\" unPublishAt_gte: \"" + now_time + "\" \n}\n    ) {\n_id\ncreatedAt\ntitle\ncontent\ntitle_en\ncontent_en\ntags\ncoverImage {\n  url\n}\ncoverImageDesc\ncoverImageDesc_en\nbannerLink\nfiles {\n  url\n  name\n  mime\n}\nfileMeta\npublishAt\n    }}"
    }
    r = requests.post('https://api-carrier.ntpu.edu.tw/strapi', data = post_data)

    return r.json()['data']['publications']

def proccess_item(item):
    # for loop with reverse
    for i in range(len(item) - 1, -1, -1):
        if check_whether_in_db(item[i]['_id']) == False:
            if item[i]['title'] == '':
                item[i]['title'] = '[此篇無標題]'
            print(item[i]['title'])
            send_mes(item[i]['title'], item[i]['_id'])
            write_in_db(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), item[i]['createdAt'], item[i]['_id'], item[i]['title'])

def init_sqlite():
    # Check the db is create, and have a table with timestamp, id, title table
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news
                    (
                        timestamp text, 
                        newsTime  text,
                        id        text, 
                        title     text
                    )''')
    conn.commit()
    conn.close()

def check_whether_in_db(id):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute("SELECT * FROM news WHERE id = '{}'".format(id))
    result = c.fetchone()
    conn.close()
    if result == None:
        return False
    else:
        return True

def write_in_db(timestamp, newsTime, id, title):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute("INSERT INTO news VALUES ('{}', '{}', '{}', '{}')".format(timestamp, newsTime, id, title))
    conn.commit()
    conn.close()

def send_mes(title, id):
    TELEGRAM_TOKEN = read_json_config()['TELEGRAM_TOKEN']
    TELEGRAM_CHAT_ID = read_json_config()['TELEGRAM_CHAT_ID']

    message = '<b>{}</b>\n<a>https://new.ntpu.edu.tw/news/{}</a>'.format(title, id)
    url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=html'.format(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, message)
    r = requests.get(url)
    print(r.text)

def read_json_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config

def write_json_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)