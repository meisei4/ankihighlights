import logging


# TODO: see the .env file for info
def configure_logging(level=logging.INFO):
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
