import redis
import uuid
import os
from urllib.parse import urlparse, urlunparse

CURRENT_CHAT_KEY = "CURRENT_CHAT_KEY"

class History:
    
    def __init__(self, args):
        print('@@@@@@@')
        print(args.get("state"))
        prefix = args.get("REDIS_PREFIX", os.getenv("REDIS_PREFIX"))
        redis_url = args.get("REDIS_URL", os.getenv("REDIS_URL"))
        print(prefix)
        print(redis_url)
        self.cache = redis.from_url(redis_url)
        
        #args.get("state") non funziona in caso di streaming
        # print('1')
        self.queue = args.get("state")
        # print('2')
        if self.queue is None or self.queue == "":
            # print('3')
            self.queue = prefix+"assistant:"+str(uuid.uuid4())
            # print(self.queue)
            # print('4')

        #non può funzionare
            # self.cache.set(prefix+CURRENT_CHAT_KEY, prefix+"assistant:"+str(uuid.uuid4()))
            # self.queue = self.cache.get(prefix + CURRENT_CHAT_KEY)
            # if self.queue is None:
            #     self.queue = prefix+"assistant:"+str(uuid.uuid4())
            
    def id(self):
        return self.queue
    
    def save(self, msg):
        self.cache.rpush(self.queue, msg)
        self.cache.expire(self.queue, 86400)
        return self.queue
        
    def load(self, ch):
        for item in self.cache.lrange(self.queue, 0, -1):
            ch.add(item.decode('utf-8'))
    
    def print(self):
        for item in self.cache.lrange(self.queue, 0, -1):
            print(item.decode('utf-8'))
            
