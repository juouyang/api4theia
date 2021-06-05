#!/bin/bash

sudo systemctl disable api4theia.service
sudo systemctl stop api4theia.service
sudo rm /lib/systemd/system/api4theia.service
sudo systemctl daemon-reload
