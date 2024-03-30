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

# Running Automaticall
To run automatically, just use a cronjob.
