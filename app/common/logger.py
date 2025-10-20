import logging
from . import var


class MyLogger(logging.Logger):
    def __init__(self, name: str):
        super().__init__(name)
        self.conn = None
        self.broadcastlevel = "info"

    def debug(self, msg, *args, **kwargs):
        return super(MyLogger, self).debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        return super(MyLogger, self).info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return super(MyLogger, self).error(msg, *args, **kwargs)


logging.setLoggerClass(MyLogger)
logger = logging.getLogger("AITG")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(message)s", "%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_debug_handler = logging.FileHandler(var.debugfile, encoding="utf-8", mode="w")
file_debug_handler.setLevel(logging.DEBUG)
file_debug_handler.setFormatter(formatter)
logger.addHandler(file_debug_handler)

file_error_handler = logging.FileHandler(var.errorfile, encoding="utf-8", mode="a")
file_error_handler.setLevel(logging.ERROR)
file_error_handler.setFormatter(formatter)
logger.addHandler(file_error_handler)
