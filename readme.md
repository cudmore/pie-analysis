This is a collection of tools to perform analysis on videos and text files saved by a [PiE server](https://github.com/cudmore/pie).

## Temperature

Python scripts to read temperature from PiE server and plot with Plotly.

The following install commands work on macOS with [Anaconda](https://www.anaconda.com/download/#macos) installed.

```
pip install pandas --upgrade
pip install ipython --upgrade
pip install ipywidgets --upgrade
pip install plotly --upgrade
```

Sometimes need this?

```
jupyter nbextension enable --py widgetsnbextension
```

## Video player

A video player to annotate videos. A work in progress.

## Commander

It is possible to run the commander on almost any machine, right now this is working on Raspberry Pis and macOS.

Clone pie

	git clone https://github.com/cudmore/pie.git

Install commander

	cd pie/commander
	./install-commander

## To Do

### Fix commander with the following

	
### 1) Modify install-commander

It is failing on fetching the ip address. Get the machine ip address on macOS

	ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}'

```
# only work on pi
#ip=`hostname -I | xargs`

# cross platform for both Pi and macOS
unamestr=`uname`
if [[ "$unamestr" == 'Linux' ]]; then
   echo "Raspberry"
   # do raspberry stuff
   ip=`hostname -I | xargs`
elif [[ "$unamestr" == 'Darwin' ]]; then
   # do macOS stuff
   echo "macOS"
   ip=`ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}'`
fi
```

It is failing on install of vitualenv environment, simple pip install vitualenv' seems to work? FIx it with ...

```
if ! type "virtualenv" > /dev/null; then
	echo '==='
	echo "=== Installing virtualenv"
	echo '==='
	
	# only work on raspberry
	sudo /usr/bin/easy_install virtualenv

	if [[ "$unamestr" == 'Linux' ]]; then
	   echo "Raspberry"
	   # do raspberry stuff
	   sudo /usr/bin/easy_install virtualenv
	elif [[ "$unamestr" == 'Darwin' ]]; then
	   # do macOS stuff
	   echo "macOS"
	   pip install virtualenv
	fi
fi
```

### 2) Modify commander.py

It is failing when trying to use bash shell command 'hostname'.

```
##################################################################
def whatismyip():
	try:
		ips = check_output(['hostname', '--all-ip-addresses'])
		ips = ips.decode('utf-8').strip()
	except:
		ips = '[IP]'
	return ips
```


### 3) We do not get systemctl on macOS, run by hand

The install-commander will give errors about installing the service, these are ok as folders just do not exist on macOS. For now the commander will not run in the background on macOS.

Run the commander by hand

```
cd commander_app
source commander_env/bin/activate
python commander_app.py
 
```

See following for how to make a .plist to run at boot and for command line to start/stop service on macOS

https://stackoverflow.com/questions/29338066/mac-osx-execute-a-python-script-at-startup

