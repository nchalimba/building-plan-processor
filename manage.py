import os
import unittest

from flask_script import Manager

from app.main import create_app

''' 
Description: This file contains the entry point into testing or running the flask application
'''

app = create_app(os.getenv('BOILERPLATE_ENV') or 'dev')

app.app_context().push()

manager = Manager(app)

@manager.command
def run():
    app.run()

@manager.command
def test():
    '''
    Description: This method runs the unit tests for the application.
    Return: result_code: int
    '''
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == '__main__':
    manager.run()
