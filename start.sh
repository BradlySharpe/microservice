#!/usr/bin/env bash

echo "Stopping..."
sudo docker-compose down

echo "Removing all images, containers, and volumes..."
#echo y | sudo docker system prune -a
# sudo docker image rm microservice-remotive
# sudo docker image rm microservice-dynamite
sudo docker image rm microservice-ziprecruiter
# sudo docker image rm microservice-sendmessage
# sudo docker image rm microservice-middleware

echo "Starting..."
sudo docker-compose up #--force-recreate