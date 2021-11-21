@echo off
REM Description: Installation file for macos and linux
echo STARTING APPLICATION...
netstat -o -n -a | findstr 6379
 
if %ERRORLEVEL% equ 0 goto FOUND
    echo "REDIS DB NOT RUNNING, TRYING TO START REDIS DB"
    docker start redisdb
    if %ERRORLEVEL% equ 0 goto REDISSTARTED
        call docker run -d --name redisdb -p 6397:6397 redis
        if %ERRORLEVEL% equ 0 goto REDISSTARTED
            echo "DOCKER DOES NOT SEEM TO BE INSTALLED, PLEASE SPIN UP A REDIS DATABASE MANUALLY"
            goto FIN
    :REDISSTARTED
    echo "REDIS DB WAS STARTED"
goto FIN
:FOUND
echo "REDIS DB IS ALREADY RUNNING"
:FIN
 
echo "INSTALLING DEPENDENCIES"
SET var=%cd%
ECHO %var%
 
pipenv --version | findstr "pipenv, version"
if %ERRORLEVEL% equ 0 goto PIPENVINSTALLED
echo "PIPENV NOT INSTALLED, INSTALLING PIPENV"
pip install pipenv
:PIPENVINSTALLED
echo "INSTALLING DEPENDENCIES"
pipenv install
echo "STARTING THE EXTRACTION BACKEND"
pipenv run flask run
pause
