import logging

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_redis import FlaskRedis
from loguru import logger

from .config import config_by_name
from .controller.data_blueprint import data_endpoints
from .controller.example_blueprint import example_endpoints
from .controller.extraction_blueprint import extraction_endpoints

''' 
Description: This file contains the main setup for the flask application
'''

flask_bcrypt = Bcrypt()
redis_client = FlaskRedis()


class InterceptHandler(logging.Handler):
    def emit(self, record):
        '''
        Description: This method handles the emission to the loguru logger and is necessary for the loguru setup
        Params: record
        '''
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


def create_app(config_name: str):
    '''
    Description: This method initializes the flask app and its dependencies
    Params: config_name: str
    Return: app: Flask
    '''
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.register_blueprint(example_endpoints, url_prefix='/api/v1/example')
    app.register_blueprint(extraction_endpoints,
                           url_prefix='/api/v1/extraction')
    app.register_blueprint(data_endpoints, url_prefix='/api/v1/data')
    flask_bcrypt.init_app(app)
    redis_client.init_app(app)

    # logging initialization
    logger.start(
        app.config["LOGDIR"] + "main.log",
        level=app.config["LOG_LEVEL"],
        format="{time} {level} {message}",
        backtrace=app.config["LOG_BACKTRACE"],
        rotation="00:00",
        compression="zip",
        filter=lambda record: "module" not in record["extra"]
    )
    # register loguru as handler
    app.logger.addHandler(InterceptHandler())
    logging.basicConfig(handlers=[InterceptHandler()], level=20)

    return app


