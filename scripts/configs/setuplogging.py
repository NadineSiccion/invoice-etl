import atexit
import json
import logging.config
from configs import mylogger

def setup_logging(config_file):
    config_file = config_file
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)