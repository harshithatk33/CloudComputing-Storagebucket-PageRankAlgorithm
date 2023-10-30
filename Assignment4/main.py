from google.cloud import storage as storage
from google.cloud import pubsub_v1
from datetime import datetime, timezone

import google.cloud.logging
import os
from flask import Flask, request
import json
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./googleCredentials.json"
import logging
import sqlalchemy
import ssl

from google.cloud import secretmanager

os.environ["INSTANCE_CONNECTION_NAME"] = "quiet-sanctuary-399018:us-central1:ds561postgresserver"
os.environ["DB_USER"] = "postgres"
os.environ["DB_NAME"] = "ds561-db"

app = Flask(__name__)

pool = ""

def getSecret(sid, vid):
    secretClient = secretmanager.SecretManagerServiceClient()
    name = f"projects/611183327365/secrets/{sid}/versions/{vid}"
    response = secretClient.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')

def createFile(fName, sid, vid):
    f = open (fName, "w")
    f.write(getSecret(sid, vid))
    f.close()

def addRequest(request):
    isBanned = "false"
    if(request.headers.get("X-country") in ["North Korea", "Iran", "Cuba", "Myanmar", "Iraq", "Libya", "Sudan", "Zimbabwe", "Syria"]):
        isBanned= "true"
    
    timeOfRequest = datetime.now(timezone.utc)
    requestedFile = "files/" + request.path.split("/")[-1]

    insertStmt = sqlalchemy.text(f"""INSERT INTO request_details (country, client_ip, gender, age, income, banned, time_of_request, requested_file) VALUES('{request.headers.get("X-country")}', '{request.headers.get("X-client-ip")}', '{request.headers.get("X-gender")}', '{request.headers.get("X-age")}', '{request.headers.get("X-income")}', {isBanned}, '{timeOfRequest}', '{requestedFile}') RETURNING request_id;""")

    res = ""

    with pool.connect() as dbConn:
        try : 
            res = dbConn.execute(insertStmt)
            dbConn.commit() 
        except:
            print("An exception occurred")
    
    return (res.fetchone()).request_id

def addError(request_id, errorCode):
    insertStmt = sqlalchemy.text(f"""INSERT INTO error_details (request_id, error_code) VALUES({request_id}, {errorCode});""")

    with pool.connect() as dbConn:
        try: 
            dbConn.execute(insertStmt)
            dbConn.commit()
        except:
            print("An exception occurred")
    return

def connectToDb():
    global pool

    createFile("server-ca.pem", "sqlserver-server-ca", "1")
    createFile("client-cert.pem", "sqlserver-client-cert", "1")
    createFile("client-key.pem", "sqlserver-client-key", "1")

    db_root_cert = "./server-ca.pem"  # e.g. '/path/to/my/server-ca.pem'
    db_cert = "./client-cert.pem"  # e.g. '/path/to/my/client-cert.pem'
    db_key = "./client-key.pem"  # e.g. '/path/to/my/client-key.pem'

    connect_args = {}

    ssl_context = ssl.SSLContext()
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.load_verify_locations(db_root_cert)
    ssl_context.load_cert_chain(db_cert, db_key)
    connect_args["ssl_context"] = ssl_context

    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username="postgres",
            password=getSecret("postgresdb-password", "1"),
            host="35.202.81.44",
            port="5432",
            database="ds561-db",
        ),
        connect_args=connect_args,
    )

connectToDb()

# @functions_framework.http
@app.route('/<filepath>', methods = ["POST","GET","PUT","PATCH","DELETE","OPTIONS"])
def cds561_hhtpRequest(filepath):

    rid = addRequest(request)

    if(request.headers.get("X-country") in ["North Korea", "Iran", "Cuba", "Myanmar", "Iraq", "Libya", "Sudan", "Zimbabwe", "Syria"]):
        # Push the message to a Pub/Sub Model topic
        pubClient = googlePubSubConnection()
        pub_payload = {"country" : str(request.headers.get("X-country")),
                    "request": str(request.method),
                    "args": str(request.args),
                    "data": str(request.data),
                    "message": "Request from an unauthorized country"}
        publishMsg(pubClient, pub_payload)
        addError(request_id=rid, errorCode=400)
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
            addError(request_id=rid, errorCode=404)
            return ("File Not Found", 404)

        # If present, retreive the file, read it and return the contents of the file with a 200 code
        return(readFileFromStorage(storageBucket, fileName), 200)
    else:
        currLog["severity"] = "INTERNAL SERVER ERROR"
        currLog["message"] = "Not Implemented method call : " + request.method
        currLog["statusCode"] = 501
        logging.warning(currLog)
        addError(request_id=rid, errorCode=501)
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))