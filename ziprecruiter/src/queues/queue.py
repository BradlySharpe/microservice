import logging
import json
from controllers.ziprecruiter import ZipRecruiter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Ensure the logger is thread safe
thread_safe_handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
thread_safe_handler.setFormatter(formatter)
logger.addHandler(thread_safe_handler)

def message_handler(ch, method, properties, body):
    message = json.loads(body.decode())

    if message is None or message.key is None:
        return
    
    zip_recruiter = ZipRecruiter(logger)

    if message.key == "CHECK_CACHE":
        return zip_recruiter.get_jobs()
    if message.key == "UPDATE":
        return zip_recruiter.fetch_zip_recruiter_jobs()

    logger.info(f"Received unknown message", message)