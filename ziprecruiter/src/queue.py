import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Ensure the logger is thread safe
thread_safe_handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
thread_safe_handler.setFormatter(formatter)
logger.addHandler(thread_safe_handler)

def messageHandler(ch, method, properties, body):
    logger.info(f"Received message: {body.decode()}")