import json

from app.main import redis_client as redis
from loguru import logger

main_logger = logger.bind()



class RedisCommands():

        def push_to_queue(self, queue, data, push_to_end=True):

            '''
            Description: This method pushes a set of data into the redis queue
            Params: queue, data, push_to_end=True
            '''
            
            queue = "queue:{}".format(queue)
            if push_to_end:
                redis.rpush(queue, json.dumps(data))
            else:
                redis.lpush(queue, json.dumps(data))
        
        def ping_redis(self):
            '''
            Description: This method pings the redis database to check if it is currently running
            Raises: ConnectionError
            '''
            try:
                redis.ping()
            except:
                main_logger.error("Failed to connect to redis database")
                raise ConnectionError
