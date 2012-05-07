import os

base = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'mysql://root:phoenix@localhost/tvchecker'
SECRET_KEY = ':\xcdl\x91\xa8\xf5\x97\xa6\xa9w\x02H' + \
             '\x1c\xffZ\xb6\xa4#\xb2\xf9\x99\xc4\x8f\xae'
#DATABASE_PATH = os.path.join(base, 'blog.db') # Can be None
#DATABASE_URL = 'sqlite:///' + DATABASE_PATH
HOST = '0.0.0.0'
PORT = 5000

LOG_FILE_PATH = 'log.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

#POSTS_PER_PAGE = 5
# Maximum amount of pages in navigation (excluding "First" and "Last" links):
#NAVIGATION_PAGE_COUNT = 5

del base
del os