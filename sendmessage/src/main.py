import os
import pika
import time
import schedule
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Ensure the logger is thread safe
thread_safe_handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
thread_safe_handler.setFormatter(formatter)
logger.addHandler(thread_safe_handler)

MESSAGE_UPDATE = {'key': 'UPDATE'}
MESSAGE_CHECK_CACHE = {'key': 'CHECK_CACHE'}

REQUIRED_ENV_VARS = [
    {"key": "QUEUE_NAMES", "type": "string"},
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

def send_message(message = MESSAGE_CHECK_CACHE):
    logger.info(f"Sending message to queues: {message}")

    connection = get_rabbitmq_connection()
    
    queue_names = os.environ['QUEUE_NAMES']
    for queue_name in queue_names.split(','):
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
        logger.info(f" [x] Sent {message} to queue '{queue_name}'")
        channel.close()

    connection.close()

ensure_environment_variables_are_configured()
ensure_rabbitmq_connection()

logger.info("Starting message sender")
time.sleep(10) # Wait for services to connect

send_message() # Force initial cache on startup

schedule.every(60).minutes.do(send_message) # Attempt to update cache every hour

while True:
    schedule.run_pending()
    time.sleep(5 * 60) # Sleep for 5 minutes