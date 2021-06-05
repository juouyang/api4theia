#!/bin/bash

WORKING_DIR="$(dirname "$PWD")"
cat <<EOF > api4theia.service
[Unit]
Description=api4theia
After=multi-user.target
[Service]
WorkingDirectory=$WORKING_DIR
Type=simple
ExecStart=/bin/sh -c "export SECRET_KEY=\$($WORKING_DIR/venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(16))'); $WORKING_DIR/venv/bin/python $WORKING_DIR/api4theia.py"
[Install]
WantedBy=multi-user.target
EOF
sudo mv ${PWD}/api4theia.service /lib/systemd/system/
sudo systemctl stop api4theia.service
sudo systemctl disable api4theia.service
sudo systemctl daemon-reload
sudo systemctl enable api4theia.service
sudo systemctl start api4theia.service