#!/usr/bin/env bash

set -euo pipefail

echo Deploying code $1 | ts


echo stopping service | ts
sudo systemctl stop tefnut.service


/home/marco/.local/bin/uv python install 3.14 >/dev/null

/home/marco/.local/bin/uv sync --extra rpi

echo Starting service| ts
sudo systemctl start tefnut.service

echo checking status| ts
if (! sudo systemctl -q is-active tefnut.service)
    then
    echo "Application failed to start"| ts
    exit -1
    else
    echo "Application started"| ts
fi
echo sleeping 60 seconds| ts
sleep 60

echo ===============================================
journalctl -n 30 -u tefnut.service
echo ===============================================



echo checking version| ts
if (journalctl -n 30 -u tefnut.service | grep -q $1 )
    then
    echo "Good version started"| ts
    else
    echo "Not on good version"| ts
    exit -1
fi

echo checking status| ts
if (! sudo systemctl -q is-active tefnut.service)
    then
    echo "Application failed after 10 seconds"| ts
    exit -1
    else
    echo "Application started after 10 seconds"| ts
fi

echo done| ts
