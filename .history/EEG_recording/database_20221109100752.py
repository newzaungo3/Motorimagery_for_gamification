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
        with self._lock:
            local_copy = self.value
            self.value = local_copy