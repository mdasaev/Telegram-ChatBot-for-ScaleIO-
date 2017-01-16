import json
import requests
import time
import logging




class SIO_Connection:


    def __init__(self,gw_ip, user,password):
        self.user = user
        self.gw_ip = gw_ip
        self.password = password
        self.logged_in = False
        self.s = requests.Session()
        self.s.headers.update({'Accept': 'application/json','Version' : '1.0'})
        self.logged_in = False
        self.sds_list =[]

    def generate_url(self,ref):
        base_url = "https://"+self.gw_ip+"/api/"
        result_url = base_url+ref
        return result_url



    def login(self):
        logging.info("Logging in with user: "+self.user+" and password "+self.password)
        self.s.auth = (self.user,self.password)
        r = self.s.get(self.generate_url("login"), verify=False)
        logging.info("Sending request: "+r.url)
        logging.info("Got response: "+r.text)
        if r.status_code == 200:
            self.logged_in = True
            self.token=r.text[1:-1] # removing double quotes on both ends after reading
        else:
            logging.info("Could not connect to SIO gateway")

    def check_login(self):
        if self.logged_in is True:
            logging.info("User is logged_in. Nothing to do")
        else:
            self.login()

    def logout(self):
        logging.info("Logging out...")
        self.s.auth = (self.user,self.token)
        r = self.s.get(self.generate_url("logout"), verify=False)
        logging.info("User "+self.user+" logged out")

    def send_query(self, query):
        self.check_login()
        logging.info("Preparing a query to gateway API")
        self.s.auth = (self.user,self.token)
        r = self.s.get(self.generate_url(query), verify=False)
        logging.info("Sending request: "+r.url)
        logging.info("Got response: "+str(r.status_code))
        if r.status_code == 200:
            data=r.json()
            for n in data:
                self.sds_list.append(n['name'])
        else:
            logging.info("Error code "+r.status_code+" from Scaleio API")
