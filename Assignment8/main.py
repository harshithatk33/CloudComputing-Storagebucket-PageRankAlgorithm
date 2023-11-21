from flask import Flask, request, make_response
from google.cloud import storage, pubsub_v1, logging as cloud_logging
from google.cloud import secretmanager
import json
import os

app = Flask(__name__)

def is_valid_country(country):
    unauthorized_countries = ["North Korea", "Iran", "Cuba", "Myanmar", "Iraq", "Libya", "Sudan", "Zimbabwe", "Syria"]
    return country not in unauthorized_countries

def connect_to_cloud_logging():
    logging_client = cloud_logging.Client()
    logging_client.setup_logging()
    return logging_client

def get_secret(secret_id, version_id):
    secret_client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/611183327365/secrets/{secret_id}/versions/{version_id}"
    response = secret_client.access_secret_version(name=secret_name)
    return response.payload.data.decode('UTF-8')

@app.route('/<filepath>', methods=["POST", "GET", "PUT", "PATCH", "DELETE", "OPTIONS"])
def handle_request(filepath):
    os.environ["ZONE"] = ""

    country_header = request.headers.get("X-country")
    if is_valid_country(country_header):
        notify_unauthorized_request(country_header)
        response = make_response("Permission Denied - Unauthorized Country", 400)
        response.headers['X-zone'] = os.environ["ZONE"]
        return response

    logging_client = connect_to_cloud_logging()
    current_log = {
        "httpRequest": {"requestMethod": request.method},
        "severity": "",
        "message": "",
        "statusCode": 000
    }

    if request.method == "GET":
        storage_client = storage.Client.create_anonymous_client()
        storage_bucket, files_in_bucket = get_storage_connection(storage_client, "cs561-assignment2-storage-bucket")
        file_name = "files/" + request.path.split("/")[-1]

        if not does_file_exist(files_in_bucket, file_name):
            current_log["severity"] = "ERROR"
            current_log["message"] = "User attempted to access non-existent file: " + file_name
            current_log["statusCode"] = 404
            log_warning(logging_client, current_log)
            response = make_response("File Not Found", 404)
            response.headers['X-zone'] = os.environ["ZONE"]
            return response

        response = make_response(read_file(storage_bucket, file_name), 200)
        response.headers['X-zone'] = os.environ["ZONE"]
        return response
    else:
        current_log["severity"] = "INTERNAL SERVER ERROR"
        current_log["message"] = "Not Implemented method call: " + request.method
        current_log["statusCode"] = 501
        log_warning(logging_client, current_log)
        response = make_response("Not Implemented yet", 501)
        response.headers['X-zone'] = os.environ["ZONE"]
        return response

def get_storage_connection(storage_client, storage_bucket_name):
    storage_bucket = storage_client.bucket(storage_bucket_name)
    files_in_bucket = [blob.name for blob in storage_bucket.list_blobs()]
    return storage_bucket, files_in_bucket

def does_file_exist(files_in_bucket, file_name):
    return file_name in files_in_bucket

def log_warning(logging_client, log_data):
    logging_client.warning(log_data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
