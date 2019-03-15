import logging, os

class DACLogger:

    def __init__(self, name : str = "DAC", path: str = f"{os.getcwd()}/dac.log"):

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        fh = None
        if len(path) > 0:
            fh = logging.FileHandler(path, mode='w', encoding="UTF-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            
    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

logger = DACLogger()