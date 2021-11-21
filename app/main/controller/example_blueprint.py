from http import HTTPStatus

from app.main.constants import QUEUE
from flask import Blueprint
from loguru import logger

''' 
Description: This file contains endpoints to test api functionalities.
'''
example_endpoints = Blueprint('example', __name__)
main_logger = logger.bind()
main_logger.disable("ezdxf")


@example_endpoints.route('/', methods=['GET'])
def example():
    '''
    Description: This method handles a sample get request to test the api and the logger.
    Return: response_message: str, http_status: int
    '''
    main_logger.debug("Example")
    return 'Hello World!', HTTPStatus.OK.value


@example_endpoints.route("/redis", methods=["GET"])
def example_redis():
    '''
    Description: This method handles a sample get request to test the api integration of redis.
    Return: response_message: str, http_status: int
    '''
    push_dto_to_redis_queue({"Hi": "Beispiel"})
    return "Hello from Redis!", HTTPStatus.OK.value

def push_dto_to_redis_queue(dto):
    from app.main.redis.redis_commands import RedisCommands
    redis_commands = RedisCommands()
    redis_commands.push_to_queue(QUEUE, dto, push_to_end=True)
