from tvchecker import app
import logging

file_path = app.config['LOG_FILE_PATH']
log_format = app.config['LOG_FORMAT']

formatter = logging.Formatter(log_format)

fh = logging.FileHandler(file_path)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
ch.setFormatter(formatter)

app.logger.addHandler(fh)
app.logger.addHandler(ch)
app.logger.setLevel(logging.DEBUG)