#! /bin/bash
sudo apt update
sudo apt -y upgrade
sudo apt-get install python3-pip -y
sudo apt-get install git -y
sudo apt-get install python3-venv -y
cd /home/htk
rm -r CloudComputing-Storagebucket-PageRankAlgorithm
rm -r Assignment8
git clone https://github.com/harshithatk33/CloudComputing-Storagebucket-PageRankAlgorithm.git
cd CloudComputing-Storagebucket-PageRankAlgorithm
pwd
cp -r /home/htk/CloudComputing-Storagebucket-PageRankAlgorithm/Assignment8 /home/htk
cd /home/htk/Assignment8
python3 -m venv env
source /home/htk/Assignment8/env/bin/activate
pip3 install -r requirements.txt
deactivate
touch Assignment8.service
echo "[Unit]
Description=Gunicorn instance to serve Assignment 8 Application
After=network.target

[Service]
User=htk
Group=www-data
WorkingDirectory=/home/htk/Assignment8
Environment="PATH=/home/htk/Assignment8/env/bin"
ExecStart=/home/htk/Assignment8/env/bin/gunicorn --workers 3 --bind 0.0.0.0:8080 wsgi:app

[Install]
WantedBy=multi-user.target" > Assignment8.service
sudo chown root:root Assignment8.service
sudo cp Assignment8.service /etc/systemd/system/Assignment8.service
sudo chown htk:htk /home/htk/Assignment8
sudo systemctl stop Assignment8
sudo systemctl daemon-reload
sudo systemctl start Assignment8
systemctl daemon-reload
sudo systemctl restart Assignment8
sudo systemctl enable Assignment8