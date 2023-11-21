from google.cloud import storage as storage
from google.cloud import pubsub_v1
from datetime import datetime, timezone

import google.cloud.logging
import os
from flask import Flask, request, make_response
import json
import logging
import sqlalchemy
import ssl

from google.cloud import secretmanager

app = Flask(__name__)

pool = ""

def ifExists(filesInBucket, fileName):
    if(fileName in filesInBucket):
        return True
    return False

def connectToCloudLogging():
    loggingClient = google.cloud.logging.Client()
    loggingClient.setup_logging()
    return loggingClient

def getSecret(sid, vid):
    secretClient = secretmanager.SecretManagerServiceClient()
    name = f"projects/611183327365/secrets/{sid}/versions/{vid}"
    response = secretClient.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')

@app.route('/<filepath>', methods = ["POST","GET","PUT","PATCH","DELETE","OPTIONS"])
def cds561_hhtpRequest(filepath):
    os.environ["ZONE"] = ""

    if(request.headers.get("X-country") in ["North Korea", "Iran", "Cuba", "Myanmar", "Iraq", "Libya", "Sudan", "Zimbabwe", "Syria"]):
        pubClient = googlePubSubConnection()
        pub_payload = {"country" : str(request.headers.get("X-country")),
                    "request": str(request.method),
                    "args": str(request.args),
                    "data": str(request.data),
                    "message": "Request from an unauthorized country"}
        publishMsg(pubClient, pub_payload)
        res = make_response("Permission Denied - Unauthorized Country", 400)
        res.headers['X-zone'] = os.environ["ZONE"]
        return res
    
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

        storageClient = connectToGoogle()
        storageBucket, filesInBucket = sbConnection(storageClient, "cs561-assignment2-storage-bucket")
        fileName = "files/" + request.path.split("/")[-1]

        if(not ifExists(filesInBucket, fileName)):
            currLog["severity"] = "ERROR"
            currLog["message"] = "User tried to search for non existant file: " + fileName
            currLog["statusCode"] = 404
            logging.warning(currLog)
            res = make_response("File Not Found", 404)
            res.headers['X-zone'] = os.environ["ZONE"]
            return res

        res = make_response(readFileFromStorage(storageBucket, fileName), 200)
        res.headers['X-zone'] = os.environ["ZONE"]
        return res
    else:
        currLog["severity"] = "INTERNAL SERVER ERROR"
        currLog["message"] = "Not Implemented method call : " + request.method
        currLog["statusCode"] = 501
        logging.warning(currLog)
        res = make_response("Not Implemented yet", 501)
        res.headers['X-zone'] = os.environ["ZONE"]
        return res

def sbConnection(storageClient, storageBucketName):
    storageBucket = storageClient.bucket(storageBucketName)
    filesInBucket = [blob.name for blob in storageBucket.list_blobs()]

    return storageBucket, filesInBucket

def googlePubSubConnection():
    pubClient = pubsub_v1.PublisherClient() 
    return pubClient

def readFileFromStorage(storageBucket, blobName):
    blob = storageBucket.blob(blobName)
    fileContent = ""

    with blob.open("r") as f:
        fileContent = f.read()
    
    return fileContent

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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))