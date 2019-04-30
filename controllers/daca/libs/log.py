import logging, os, datetime

class DACLogger:

    bufferLenght = 50

    def __init__(self, name : str = "DAC", path: str = f"{os.getcwd()}/dac.{datetime.datetime.now():%Y-%m-%dT%H-%M-%S}.log"):

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        fh = logging.FileHandler(path, mode='w', encoding="UTF-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        self.buffer = []

    def info(self, message: str):
        if not self.logger.disabled:
            self.buffer.append(message)
            if len(self.buffer) > DACLogger.bufferLenght:
                self.__log()        

    def __log(self):
        m = '\n'.join([ f'{s}' for s in self.buffer])
        self.logger.info(m)
        self.buffer.clear()

    def flush(self):
        if not self.logger.disabled:
            self.__log()

    def suppress(self, boolean:bool):
        self.logger.disabled = boolean

logger = DACLogger()