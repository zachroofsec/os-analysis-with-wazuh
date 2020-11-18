#!/bin/sh

while ! nc -zvu merlin-server 443; do
  echo "Waiting for Merlin server to come up"
  sleep 1
done

/opt/merlin/merlinAgent-Linux-x64 -v \
  --url https://merlin-server:443 \
  --proto http3 > /var/log/merlin/merlin.log 2>&1 &

