#!/bin/bash
echo "Containerization is started with bare-metal repository"
docker build -t 10.15.1.132:30000/ebv/cxm-websocket:latest --network=host .
docker push 10.15.1.132:30000/ebv/cxm-websocket:latest
echo "Containerization is finished with bare-metal repository"

echo "Containerization backup is in progress with Azure repository"
docker tag 10.15.1.132:30000/ebv/cxm-websocket:latest 10.15.1.132:30001/ebv/cxm-websocket:latest
docker push 10.15.1.132:30001/ebv/cxm-websocket:latest
echo "Containerization backup is done with Azure repository"