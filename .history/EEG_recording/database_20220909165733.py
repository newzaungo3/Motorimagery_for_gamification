from threading import Thread,Lock
import time
import logging
import requests

class Database:
    def __init__(self,values):
        self.value = values
        self._lock = Lock()
        self.str = "Hello"

    def locked_update(self, name):
        
        logging.info("Thread %s: starting update", name)
        logging.debug("Thread %s about to lock", name)
        with self._lock:
            logging.debug("Thread %s has lock", name)
            local_copy = self.value
            self.value = local_copy
            time.sleep(0.5)
            data = {
            "name":"New",
            "data": self.value.tolist()
            }
            requests.post("http://localhost:8000/items",json=data)
            logging.debug("Thread %s about to release lock", name)
        logging.debug("Thread %s after release", name)
        logging.info("Thread %s: finishing update", name)