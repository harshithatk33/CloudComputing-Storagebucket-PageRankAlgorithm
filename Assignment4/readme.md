gcloud compute instances create htk-assignment4-publisher-vm --project=quiet-sanctuary-399018 --zone=us-central1-a --machine-type=e2-micro --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default --metadata=startup-script=\#\!\ /bin/bash$'\n'sudo\ apt\ update$'\n'sudo\ apt\ -y\ upgrade$'\n'sudo\ apt-get\ install\ python3-pip\ -y$'\n'sudo\ apt-get\ install\ git\ -y$'\n'sudo\ apt-get\ install\ python3-venv\ -y$'\n'cd\ /home/htk$'\n'rm\ -r\ CloudComputing-Storagebucket-PageRankAlgorithm$'\n'rm\ -r\ Assignment4$'\n'git\ clone\ https://github.com/harshithatk33/CloudComputing-Storagebucket-PageRankAlgorithm.git$'\n'cd\ CloudComputing-Storagebucket-PageRankAlgorithm$'\n'pwd$'\n'cp\ -r\ /home/htk/CloudComputing-Storagebucket-PageRankAlgorithm/Assignment4\ /home/htk$'\n'cd\ /home/htk/Assignment4$'\n'python3\ -m\ venv\ env$'\n'source\ /home/htk/Assignment4/env/bin/activate$'\n'pip3\ install\ -r\ requirements.txt$'\n'deactivate$'\n'touch\ Assignment4.service$'\n'echo\ \"\[Unit\]$'\n'Description=Gunicorn\ instance\ to\ serve\ Assignment\ 4\ app$'\n'After=network.target$'\n'$'\n'\[Service\]$'\n'User=htk$'\n'Group=www-data$'\n'WorkingDirectory=/home/htk/Assignment4$'\n'Environment=\"PATH=/home/htk/Assignment4/env/bin\"$'\n'ExecStart=/home/htk/Assignment4/env/bin/gunicorn\ --workers\ 3\ --bind\ 0.0.0.0:8080\ wsgi:app$'\n'$'\n'\[Install\]$'\n'WantedBy=multi-user.target\"\ \>\ Assignment4.service$'\n'sudo\ chown\ root:root\ Assignment4.service$'\n'sudo\ cp\ Assignment4.service\ /etc/systemd/system/Assignment4.service$'\n'sudo\ systemctl\ stop\ Assignment4$'\n'sudo\ systemctl\ daemon-reload$'\n'sudo\ systemctl\ start\ Assignment4$'\n'systemctl\ daemon-reload$'\n'sudo\ systemctl\ restart\ Assignment4$'\n'sudo\ systemctl\ enable\ Assignment4248 --maintenance-policy=MIGRATE --provisioning-model=STANDARD --service-account=cds561-assignment3@quiet-sanctuary-399018.iam.gserviceaccount.com --scopes=https://www.googleapis.com/auth/cloud-platform --tags=http-server-8080,http-server,https-server --create-disk=auto-delete=yes,boot=yes,device-name=htk-assignment4-publisher-vm,image=projects/ubuntu-os-cloud/global/images/ubuntu-2004-focal-v20230918,mode=rw,size=10,type=projects/quiet-sanctuary-399018/zones/us-central1-a/diskTypes/pd-balanced --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --labels=goog-ec-src=vm_add-gcloud --reservation-affinity=any

gcloud compute addresses create harshu-a4-ip-address \
 --region=us-central1

gcloud compute addresses describe harshu-a4-ip-address

gcloud compute instances create assignment4-http-vm --address=34.27.2.159 --zone=us-central1-a

gcloud compute instances describe assignment4-http-vm

gcloud compute instances delete-access-config htk-assignment4-publisher-vm \
 --access-config-name="External NAT" \
 --zone=us-central1-a

gcloud compute instances add-access-config htk-assignment4-publisher-vm \
--access-config-name="Exteral Static IP" --address=34.28.125.248 \
--zone=us-central1-a

address: 34.28.125.248

gunicorn --bind 0.0.0.0:8080 wsgi:app
