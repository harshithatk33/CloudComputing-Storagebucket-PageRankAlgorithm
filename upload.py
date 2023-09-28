import os
from google.cloud import storage as storage

def main():
    global pageGraph
    global pageRank
    global sumPageRank
    from google.cloud import storage


    sumPageRank = (0.15 * 10000)
    pageRank = dict()
    pageGraph = dict()
    googleClient = storage.Client.create_anonymous_client()
    print("Client Created")
    # Upload the generated files to the bucket
    for root, _, files in os.walk("fileGeneration"):
        for file in files:
            local_path = os.path.join(root, file)
            bucket = googleClient.bucket("cds561-assignment2-harshitha")
            blob = bucket.blob(os.path.join("fileGeneration", file))
            blob.upload_from_filename(local_path)
    # storageBucket, filesInBucket = readStorageBucket(googleClient, "cs561-assignment2-storage-bucket")
    # operationsForMetrics(storageBucket, filesInBucket)

if __name__ == "__main__":
    main()