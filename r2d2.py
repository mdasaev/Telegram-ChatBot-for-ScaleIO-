import json
import requests
import time
import urllib
from dbhelper import DBHelper
from classes.ScaleIO_connection import SIO_Connection
import logging

TOKEN = "245861285:AAG-5Bc9YkPyYBtMJf6OTrN3S3qasQ1aODQ"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
db = DBHelper()

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=0):
    url = URL + "getUpdates?timeout=10"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)

    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    logging.info(url)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def handle_updates(updates,SIO_Connection):

    sio=SIO_Connection

    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            if text == "/done":
                sio.logout()
                send_message("User"+sio.user+" logged out", chat)
            elif text == "/start":
                send_message("Welcome to your personal ScaleIO Assistant. Type a request you want to send. Type /done to logout", chat)
            else:
            #here we start the job
                sio.sds_list=[]
                sio.send_query("types/Sds/instances")
                str="List of SDS:\n"+'\n'.join(sio.sds_list)
                logging.info(str)

                send_message(str,chat)

        except KeyError:
            print("Please use a text or emoji")

def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def main():
    last_update_id = None
    #sio part
    sio = SIO_Connection("192.168.0.110:443", "admin","Lfcftd123")
    logging.basicConfig(filename='sio_agent.log', level=logging.INFO) #TODO add timestamp
    logging.info("Starting SIO api requester")
    #sio.send_query("types/Sds/instances")

    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            #print(last_update_id)
            handle_updates(updates,sio)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
