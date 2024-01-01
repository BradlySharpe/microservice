import os
import pika
import time
import threading
import logging
from flask import Flask
from route import getFetch
from queue import messageHandler

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Ensure the logger is thread safe
thread_safe_handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
thread_safe_handler.setFormatter(formatter)
logger.addHandler(thread_safe_handler)

REQUIRED_ENV_VARS = [
    {"key": "API_PORT", "type": "number"},
    {"key": "ENDPOINT_API", "type": "string"},
    {"key": "CACHE_REDIS_KEY", "type": "string"},
    {"key": "REDIS_EXPIRY_SECONDS", "type": "number"},
    {"key": "QUEUE_JOBS", "type": "string"},
]

def ensure_environment_variables_are_configured():
    errors = []

    for variable in REQUIRED_ENV_VARS:
        key = variable["key"]
        value = os.environ.get(key, "").strip()

        if not value:
            errors.append(f"  - {key} is not configured")
        elif variable["type"] == "number":
            try:
                int(value)
            except ValueError:
                errors.append(f"  - {key} is not set to a valid number: '{value}'")

    if errors:
        raise ValueError("Unable to start as the following environment variables are not configured appropriately:\n" + "\n".join(errors))

def get_rabbitmq_connection():
    connection_params = pika.ConnectionParameters(host='rabbitmq', port=5672)
    connection = None

    while connection is None:
        try:
            connection = pika.BlockingConnection(connection_params)
            if (connection.is_closed):                
                connection.close()
                connection = None
                raise Exception("Connection is not open")
        except Exception as ex:
            logger.error("Error connecting to RabbitMQ - waiting for service to start")
            time.sleep(2)

    return connection

def ensure_rabbitmq_connection():
    try:
        connection = get_rabbitmq_connection()
        connection.close()
    except Exception as ex:
        logger.error("An error occurred while ensuring rabbitmq was connected", ex)

def create_queue_listener():
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()

        queue_name = os.environ['QUEUE_JOBS']
        channel.queue_declare(queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=messageHandler, auto_ack=True)

        logger.info("Starting to consume messages")
        channel.start_consuming()
    except Exception as ex:
        logger.error("An error occurred while creating the queue listener", ex)

@app.route('/fetch', methods=['GET'])
def handle_fetch_request():
    logger.info("Handling fetch request")
    return getFetch()

def create_api():
    try:
        os.system(f"gunicorn -w 1 -b 0.0.0.0:{os.environ['API_PORT']} main:app")
    except Exception as ex:
        logger.error("An error occurred while creating the API", ex)

def init():
    try:
        ensure_environment_variables_are_configured()
        ensure_rabbitmq_connection()

        queue_thread = threading.Thread(target=create_queue_listener)
        queue_thread.start()
        logger.info("Queue Thread running")

        api_thread = threading.Thread(target=create_api)
        api_thread.start()
        logger.info("API Thread running")

        logger.info("ZipRecruiter running")

        api_thread.join() # Quit once the API thread exits
        exit()
    except Exception as ex:
        logger.error(f"Error starting ZipRecruiter: {ex}")
        # Ensure the process quits fully so it will be restarted by Docker
        exit(-1)

# Run the asyncio event loop
if __name__ == "__main__":
    init()