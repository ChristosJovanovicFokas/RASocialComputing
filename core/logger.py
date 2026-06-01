import logging
from datetime import datetime

class Logger:
    def __init__(self, name="scraper", log_file="data/scraper.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s"
            )

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def success(self, url, status_code, response_time):
        self.logger.info(
            f"(SUCCESS) {url} | Status: {status_code} | Time: {response_time:.2f}s"
        )
    
    def failure(self, url, error):
        self.logger.error(f"(!!!FAILURE!!!) {url} | Error: {error}")