import os

''' 
Description: This file contains configuration settings for the dev, testing and prod stage of the application
'''
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret_key')
    DEBUG = False
    REDIS_URL = "redis://:@localhost:6379/0"
    LOGDIR = os.getcwd() + "/logs/"
    LOG_LEVEL = "DEBUG"
    LOG_BACKTRACE = True


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY
