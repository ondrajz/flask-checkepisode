import os

base = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'DBTYBE://NAME:PASSWORD@SERVER/DBNAME'
SECRET_KEY = 'yourboring' + \
             'secretkey'
             
HOST = '0.0.0.0'
PORT = 5000
DEBUG = False

LOG_FILE_PATH = 'log.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

del base
del os