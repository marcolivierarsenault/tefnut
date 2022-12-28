#! /bin/bash

echo Deploying code $1


echo stopping service
systemctl stop tefnut.service

cd /home/marco/tefnut
echo updating code
git checkout main
git pull --all
echo checkout specific code
git checkout $1

/home/marco/.local/bin/poetry install

echo Starting service
systemctl start tefnut.service

echo ===============================================
journalctl -n 30 -u tefnut.service
echo ===============================================
sudo systemctl status tefnut.service
echo ===============================================

echo done
