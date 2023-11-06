import sqlalchemy
import pandas as pd
from google.cloud.sql.connector import Connector, IPTypes
import pg8000

import os
import ssl
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./googleCredentials.json"

os.environ["INSTANCE_CONNECTION_NAME"] = "quiet-sanctuary-399018:us-central1:ds561postgresserver"
os.environ["DB_USER"] = "postgres"
os.environ["DB_NAME"] = "ds561-db"
os.environ["DB_PASS"] = "assignmentds561password"


instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"] # e.g. 'project:region:instance'
db_user = os.environ["DB_USER"] # e.g. 'my-db-user'
db_pass = os.environ["DB_PASS"] # e.g. 'my-db-password'
db_name = os.environ["DB_NAME"] # e.g. 'my-database'

db_root_cert = "./server-ca.pem"  # e.g. '/path/to/my/server-ca.pem'
db_cert = "./client-cert.pem"  # e.g. '/path/to/my/client-cert.pem'
db_key = "./client-key.pem"  # e.g. '/path/to/my/client-key.pem'

connect_args = {}

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
ssl_context.verify_mode = ssl.CERT_REQUIRED
ssl_context.load_verify_locations(db_root_cert)
ssl_context.load_cert_chain(db_cert, db_key)
connect_args["ssl_context"] = ssl_context

pool = sqlalchemy.create_engine(
    sqlalchemy.engine.url.URL.create(
        drivername="postgresql+pg8000",
        username="postgres",
        password=db_pass,
        host="35.202.81.44",
        port="5432",
        database="ds561-db",
    ),
    connect_args=connect_args,
)

query = "SELECT ip, country FROM accesslogs;"
df = pd.read_sql(query, pool)


from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

df['ip'] = df['ip'].astype(int)

X = df['ip'].values.reshape(-1, 1)
y = df['country']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the Random Forest model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Evaluate the model
accuracy = rf_model.score(X_test, y_test)
print(f"Model accuracy: {accuracy*100:.2f}%")