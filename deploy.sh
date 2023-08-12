#! /bin/bash

echo Deploying code $1


echo stopping service
systemctl stop tefnut.service


/home/marco/.local/bin/poetry install

echo Starting service
systemctl start tefnut.service

if (! systemctl -q is-active tefnut.service)
    then
    echo "Application failed to start"
    exit -1
fi

echo ===============================================
journalctl -n 30 -u tefnut.service
echo ===============================================

echo sleeping 10 seconds
sleep 10
if (! systemctl -q is-active tefnut.service)
    then
    echo "Application failed after 10 seconds"
    exit -1
fi

echo done
