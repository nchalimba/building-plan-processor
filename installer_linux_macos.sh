#!/bin/bash
#Description: Installation file for macos and linux
cd "$(dirname "$0")"
echo "CHECKING IF REDIS DATABASE INSTANCE IS RUNNING"
echo ""
if lsof -i :6379 | grep -q 'COMMAND'; then
    echo "REDIS DATABASE IS ALREADY RUNNING"
    echo ""
else
    echo "CHECK IF DOCKER IS INSTALLED"
    echo ""
    if docker -v | grep -q "command not found"; then
        echo "DOCKER DOES NOT SEEM TO BE INSTALLED, PLEASE SPIN UP A REDIS DATABASE MANUALLY"
        echo ""
    else
        echo "TRYING TO START REDIS CONTAINER"
        echo ""
        if ! docker start redisdb ; then
            echo "REDIS CONTAINER DOES NOT EXIST, CREATING NEW REDIS CONTAINER..."
            echo ""
            docker run -d --name redisdb -p 6379:6379 redis
            docker start redisdb
            echo "STARTED REDIS CONTAINER"
            echo ""
        fi
    fi
fi

echo "CHECKING IF PIPENV IS INSTALLED"
echo ""
if pipenv --version | grep -q "command not found"; then
    echo "PIPENV IS NOT INSTALLED, INSTALLING PIPENV..."
    echo ""
    if pip install pipenv | grep -q "command not found"; then
        echo "PIP IS NOT INSTALLED, PLEASE INSTALL PIP AND PIPENV MANUALLY"
        echo ""
    fi
fi

echo "INSTALLING ALL DEPENDENCIES..."
echo ""
pipenv install
echo "STARTING THE EXTRACTION BACKEND..."
echo ""
pipenv run flask run
read -n 1 -p "Press any key to exit" maininput