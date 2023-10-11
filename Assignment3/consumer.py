import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/htk/personal/Fall2023_semester/CDS_561_CloudComputing/Assignments/Assignment2/googleCredentials.json"
import json
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
import time

# GCP topic, project & subscription ids
PUB_SUB_TOPIC = "cds561_Assignment3"
PUB_SUB_PROJECT = "quiet-sanctuary-399018"
PUB_SUB_SUBSCRIPTION = "cds561_Assignment3-sub"

# Pub/Sub consumer timeout
consumerTimeout = 3.0

def payloadProcessor(message):
    print(f"Received the message from pub : {message.data}.")
    message.ack()  

def consumer(project, subscription, callback, period):
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(project, subscription)
        print(f"Listening for messages on {subscription_path}..\n")
        streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
        # Wrap subscriber in a 'with' block to automatically call close() when done.
        with subscriber:
            try:
                # When `timeout` is not set, result() will block indefinitely,
                # unless an exception is encountered first.                
                streaming_pull_future.result(timeout=period)
            except TimeoutError:
                streaming_pull_future.cancel()


while (True):
     print("-----------")
     consumer(PUB_SUB_PROJECT, PUB_SUB_SUBSCRIPTION, payloadProcessor, consumerTimeout)
     time.sleep(3)