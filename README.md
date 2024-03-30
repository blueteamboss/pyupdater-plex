# Support
This currently only supports Plex running on Debian/Ubuntu derivatives. Future support for others will be added.

# Installing
To install, create a directory `/opt/scripts/pyupdater-plex`, initialize a virtual environment, and install requirements.

```sh
mkdir /opt/scripts/pyupdater-plex
python3 -m venv /opt/scripts/pyupdater-plex/venv
source /opt/scripts/pyupdater-plex/venv/bin/activate
pip install -m requirements.txt
cp config.yml /opt/scripts/pyupdater-plex/config.yml
cp updater.py /opt/scripts/pyupdater-plex/updater.py
cp plex-updater-runner.sh /opt/scripts/pyupdater-plex/plex-updater-runner.sh
chmod +x /opt/scripts/pyupdater-plex/plex-updater-runner.sh
```

# Running
Just run:
```
bash /opt/scripts/pyupdater-plex/plex-updater-runner.sh
```

# Running Automatically
To run automatically, just use a cronjob.

# Config File
The config file can be changed (not now, in the future) to support other distros/package managers, as well as using beta release channels. Right now, none of that is in use, but there are plans to add that in the future.