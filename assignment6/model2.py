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

query = "SELECT * FROM accesslogs;"
df = pd.read_sql(query, pool)

print(df)


import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

income_mapping = {
    '0-10k': 5000, '10k-20k': 15000, '20k-40k': 30000, '40k-60k': 50000, '60k-100k': 80000, 
    '100k-150k': 125000, '150k-250k': 200000, '250k+': 250000
}

age_mapping = {
    '0-16': 0, '17-25': 1, '26-35': 2, '36-45': 3, 
    '46-55': 4, '56-65': 5, '66-75': 6, '76+': 7
}

df['income'] = df['income'].map(income_mapping).values.reshape(-1, 1)
df['age'] = df['age'].map(age_mapping).values.reshape(-1, 1)

label_encoder = LabelEncoder()
df['country'] = label_encoder.fit_transform(df['country'])

df['ip'] = df['ip'].astype(int)
df['gender'] = df['gender'].astype(int)

df['ip'] = df['ip'].values.reshape(-1, 1)
df['gender'] = df['gender'].values.reshape(-1, 1)

X = df[['ip', 'country', 'age', 'gender']]
y = df['income']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)


rf_model = RandomForestClassifier(n_estimators=100, random_state=42)

rf_model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = rf_model.predict(X_test)

accuracy = rf_model.score(X_test, y_test)
print(f"Model accuracy: {accuracy*100:.2f}%")

accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy*100:.2f}%")

