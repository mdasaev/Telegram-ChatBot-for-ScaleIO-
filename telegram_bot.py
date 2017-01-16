import json
import requests
import time
import urllib
#from classes.ScaleIO_connection import SIO_Connection
import logging


class ChatBot:

    def __init__(self,chat_id=None,token=None, url="https://api.telegram.org/bot", timeout=100):
        self.token = token
        self.url = "{}/".format(token)
        self.s = requests.Session()
        self.chat_id = chat_id
        self.last_update_id = 0
        self.updates=[]
        self.session_timeout=timeout
        self.greeting = "Welcome to your personal ScaleIO Assistant. Choose a request you want to send. Type /done to complete session"

    def generate_url(self,resf):
        logging.info("Generating URL request for Telegram API")
        base_url = self.url
        result_url = base_url+ref
        logging.info("URL generated: {}".format(result.url))
        return result_url

    def send_query(self,query):
        response = self.s.get(self.generate_url(query))
        logging.info("URL generated: {}".format(response.url))

        content = response.content.decode("utf8")
        return content

    def get_json_from_url(query):
        content = self.send_query(query)
        logging.info("Loading JSON from response")
        js = json.loads(content)
        return js

    def get_updates(self,offset=0):
        url = self.generate_url("getUpdates?timeout={}".format(self.session_timeout))
        if offset:
            url += "&offset={}".format(offset)
        js = self.get_json_from_url(url)
        return js

    def get_last_update_id(updates):
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        logging.info("Current max update_id is {}".format(max(update_ids)))
        return max(update_ids)

    def get_last_chat_id_and_text(updates):
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        logging.info("Last chat_id {} and text is {}".format(chat_id,text))
        return (text, chat_id)


    def send_message(self,text, chat_id, reply_markup=None):
        text = urllib.parse.quote_plus(text)
        logging.info("Sending a message to chat owner: {}".format(text))
        url = self.generate_url("sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id))
        r_url= url.replace('[','(')
        r_url= url.replace(']',')')
        logging.info("To make sure that URL is correct: {}".format(r_url))

        if reply_markup:
            r_url += "&reply_markup={}".format(reply_markup)
        self.send_query(r_url)

    def handle_updates(self,updates,sio):

        for update in updates["result"]:
            try:
                text = update["message"]["text"]
                chat = update["message"]["chat"]["id"]
                if text == "/done":
                    logging.info("Got request from chat owner to logout")
                    sio.logout()
                    self.send_message("User"+sio.user+" logged out", chat)
                elif text == "/start":
                    self.send_message(self.greeting, chat)
                else:
                #here we start the job
                    sio.sds_list=[]
                    sio.send_query("types/Sds/instances")
                    tmp="List of SDS:\n"+'\n'.join(sio.sds_list)
                    logging.info("Temporary logging: {}".format(tmp))

                    self.send_message(str,chat)

            except KeyError:
                print("Please use a text or emoji")

    def build_keyboard(items):
        keyboard = [[item] for item in items]
        reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
        logging.info("Keyboard preview: {}".format(reply_markup))
        return json.dumps(reply_markup)
