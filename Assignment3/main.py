from google.cloud import storage as storage
from google.cloud import pubsub_v1

import google.cloud.logging
import functions_framework
import flask
import os
import json
import logging

@functions_framework.http
def cds561_hhtpRequest(request: flask.Request) -> flask.typing.ResponseReturnValue:

    if(request.headers.get("X-country") in ["North Korea", "Iran", "Cuba", "Myanmar", "Iraq", "Libya", "Sudan", "Zimbabwe", "Syria"]):
        # Push the message to a Pub/Sub Model topic
        pubClient = googlePubSubConnection()
        pub_payload = {"country" : str(request.headers.get("X-country")),
                    "request": str(request.method),
                    "args": str(request.args),
                    "data": str(request.data),
                    "message": "Request from an unauthorized country"}
        publishMsg(pubClient, pub_payload)
        return ("Permission Denied - Unauthorized Country", 400)
    
    loggingClient = connectToCloudLogging()
    currLog = {
        "httpRequest":{
            "requestMethod": request.method
        },
        "severity": "",
        "message": "",
        "statusCode": 000
    }

    if request.method == "GET":

        # Connect to google storage if not already connected
        storageClient = connectToGoogle()
        storageBucket, filesInBucket = sbConnection(storageClient, "cs561-assignment2-storage-bucket")
        fileName = fileName = "files/" + request.path.split("/")[-1]

        
        # Get the file name and check if the file is present in the bucket
        if(not ifExists(filesInBucket, fileName)):
            currLog["severity"] = "ERROR"
            currLog["message"] = "User tried to search for non existant file: " + fileName
            currLog["statusCode"] = 404
            logging.warning(currLog)
            return ("File Not Found", 404)

        # If present, retreive the file, read it and return the contents of the file with a 200 code
        return(readFileFromStorage(storageBucket, fileName), 200)
    else:
        currLog["severity"] = "INTERNAL SERVER ERROR"
        currLog["message"] = "Not Implemented method call : " + request.method
        currLog["statusCode"] = 501
        logging.warning(currLog)
        return ("Not Implemented yet", 501)




def sbConnection(storageClient, storageBucketName):
    storageBucket = storageClient.bucket(storageBucketName)
    filesInBucket = [blob.name for blob in storageBucket.list_blobs()]

    return storageBucket, filesInBucket

def googlePubSubConnection():
    pubClient = pubsub_v1.PublisherClient() 
    return pubClient

def ifExists(filesInBucket, fileName):
    if(fileName in filesInBucket):
        return True
    return False

def readFileFromStorage(storageBucket, blobName):
    blob = storageBucket.blob(blobName)
    fileContent = ""

    with blob.open("r") as f:
        fileContent = f.read()
    
    return fileContent

def connectToCloudLogging():
    loggingClient = google.cloud.logging.Client()
    loggingClient.setup_logging()
    return loggingClient

def connectToGoogle():
    storageClient = storage.Client.create_anonymous_client()
    return storageClient
    
def publishMsg(pubClient, payload):
    PUB_SUB_TOPIC = "cds561_Assignment3"
    PUB_SUB_PROJECT = "quiet-sanctuary-399018"

    topicPath = pubClient.topic_path(PUB_SUB_PROJECT, PUB_SUB_TOPIC)        
    jsonData = json.dumps(payload).encode("utf-8")           
    future = pubClient.publish(topicPath, data=jsonData)
    print("Pushed message to topic.")   
    return