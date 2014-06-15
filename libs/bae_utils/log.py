# -*- coding: utf-8 -*-

import os.path
import logging
import logging.handlers

def getLogger(file_name, file_path = "/home/bae/log", max_bytes = 20971520):
    logger = logging.Logger("bae")
    handler = logging.handlers.RotatingFileHandler(os.path.join(file_path, file_name), maxBytes = max_bytes)
    formatter = "%(levelname)s %(module)s %(asctime)s %(message)s"
    handler.setFormatter(logging.Formatter(formatter))
    logger.addHandler(handler)
    return logger
