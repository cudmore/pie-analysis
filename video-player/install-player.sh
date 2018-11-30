#!/bin/bash

# Author: Robert H Cudmore
# Date: 20180603
#
# Purpose: Bash script to install video-player

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

if [ $(id -u) = 0 ]; then
   echo "Do not run with sudo. Try again without sudo"
   exit 1
fi

if ! type "virtualenv" > /dev/null; then
	echo '==='
	echo "=== install-player: Installing virtualenv"
	echo '==='
	#sudo /usr/bin/easy_install virtualenv
	#pip install virtualenv
	sudo apt-get -qy install python-virtualenv
fi

if [ ! -d "player_env/" ]; then
	echo '==='
	echo "=== install-player: Making Python 3 virtual environment in $PWD/player_env"
	echo '==='
	if ! type "virtualenv" > /dev/null; then
		echo -e 'install-player: ${RED}ERROR${NC}: DID NOT INSTALL VIRTUALENV -->> ABORTING'
		exit 0
	else
		mkdir player_env
		virtualenv -p python3 --no-site-packages player_env
	fi
else
	echo '==='
	echo "=== install-player: Python 3 virtual environment already exists in $PWD/player_env"
	echo '==='
fi



if [ -f "player_env/bin/activate" ]; then
	echo '==='
	echo "=== install-player: Activating Python 3 virtual environment with 'source player_env/bin/activate'"
	echo '==='
	source player_env/bin/activate
else
	echo -e "${RED}ERROR${NC}: Python 3 virtual environment did not install in $PWD/player_env"
	echo "Make sure virtualenv is installed and try installing again"
	exit 1
fi


echo '==='
echo "=== install-player: Installing required python libraries with 'pip install -r requirements.txt'"
echo '==='
pip install -r requirements.txt

echo '==='
echo "=== install-player: Deactivating Python 3 virtual environment with 'deactivate'"
echo '==='
deactivate

# done
echo -e "${GREEN}Success${NC}: The video-player is installed."
echo "Run the video-player with 'player'"
