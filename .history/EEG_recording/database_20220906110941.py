from threading import Thread,Lock
import time
import logging

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
            local_copy += 1
            time.sleep(0.1)
            self.value = local_copy
            logging.debug("Thread %s about to release lock", name)
        logging.debug("Thread %s after release", name)
        logging.info("Thread %s: finishing update", name)