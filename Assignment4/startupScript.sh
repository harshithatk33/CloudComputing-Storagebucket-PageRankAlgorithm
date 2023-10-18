#! /bin/bash
sudo apt update
sudo apt -y upgrade
sudo apt-get install python3-pip -y
sudo apt-get install git -y
sudo apt-get install python3-venv -y
cd /home/htk
rm -r CloudComputing-Storagebucket-PageRankAlgorithm
rm -r Assignment4
git clone https://github.com/harshithatk33/CloudComputing-Storagebucket-PageRankAlgorithm.git
cd CloudComputing-Storagebucket-PageRankAlgorithm
pwd
cp -r /home/htk/CloudComputing-Storagebucket-PageRankAlgorithm/Assignment4 /home/htk
cd /home/htk/Assignment4
python3 -m venv env
source /home/htk/Assignment4/env/bin/activate
pip3 install -r requirements.txt
deactivate
touch Assignment4.service
echo "[Unit]
Description=Gunicorn instance to serve Assignment 4 app
After=network.target

[Service]
User=htk
Group=www-data
WorkingDirectory=/home/htk/Assignment4
Environment="PATH=/home/htk/Assignment4/env/bin"
ExecStart=/home/htk/Assignment4/env/bin/gunicorn --workers 3 --bind 0.0.0.0:8080 wsgi:app

[Install]
WantedBy=multi-user.target" > Assignment4.service
sudo chown root:root Assignment4.service
sudo cp Assignment4.service /etc/systemd/system/Assignment4.service
sudo systemctl stop Assignment4
sudo systemctl daemon-reload
sudo systemctl start Assignment4
systemctl daemon-reload
sudo systemctl restart Assignment4
sudo systemctl enable Assignment4