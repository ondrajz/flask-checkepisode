from flask import Flask

app = Flask(__name__)
app.config.from_object('real_config')
# this needs to be changed to config

import models
import friendly_time
import views
import login
import logger

def run():
    app.debug=app.config['DEBUG']
    app.run(host=app.config['HOST'], port=app.config['PORT'])