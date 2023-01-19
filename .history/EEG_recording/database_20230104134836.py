from threading import Thread,Lock
import time
import logging
import requests

class Database:
    def __init__(self,train,label,names):
        self.train = train
        self.label = label
        self._lock = Lock()
        self.str = names

    def locked_update(self, name):
        local_copy = self.value
        local_copy2 = self.str
        self.value = local_copy
        self.str =  local_copy2