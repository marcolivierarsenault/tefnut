#! /bin/bash

echo Deploying code $1


echo stopping service
sudo systemctl stop tefnut.service


/home/marco/.local/bin/poetry install

echo Starting service
sudo systemctl start tefnut.service

if (! sudo systemctl -q is-active tefnut.service)
    then
    echo "Application failed to start"
    exit -1
    else
    echo "Application started"
fi

echo ===============================================
journalctl -n 30 -u tefnut.service
echo ===============================================

echo sleeping 10 seconds

if (journalctl -n 30 -u tefnut.service | grep -q $1 )
    then
    echo "Good version started"
    else
    echo "Not on good version"
    exit -1
fi

sleep 10
if (! sudo systemctl -q is-active tefnut.service)
    then
    echo "Application failed after 10 seconds"
    exit -1
    else
    echo "Application started after 10 seconds"
fi

echo done
