"""
    Python updater script for Plex Automatic Updates
"""
import json
import subprocess
import re
import hashlib
import requests
import yaml

class PlexAutoUpdater:
    """
        This method handles updating Plex automatically
    """
    def __init__(self, config_path: str) -> None:
        self.configs = self.load_config(config_path)

    def load_config(self, config_path: str) -> dict | bool:
        """
            Loads the config file using yaml safe load
        """
        try:
            with open(config_path, 'r', encoding='UTF-8') as file:
                data = yaml.safe_load(file)
            return data
        except FileNotFoundError as e:
            print(f"Could not find config file: {e}")
        except OSError as e:
            print(f"OS Exception while loading config file: {e}")
        return False

    def download_file(self, url: str, output_file: str) -> bool:
        """
            Performs a file download using requests
            lib and implements basic error handling
        """
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(output_file, 'wb') as file:
                    file.write(response.content)
            else:
                print(f"Download failed, received non-success status code: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection Error: Could not download file: {e}")
        except requests.exceptions.Timeout as e:
            print(f"Network Error: Request Timed Out, Check Connection: {e}")
        except requests.exceptions.RequestException as e:
            print(f"A catastrophic failure occured when trying to download the file: {e}")
        except OSError as e:
            print(f"OS Exception: {e}")
        else:
            print(f"Successfully downloaded {url} --> {output_file}")
            return True
        return False

    def download_large_file(self, url: str, output_file: str) -> bool:
        """
            Downloads a large file in 8192 byte chunks
        """
        try:
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                with open(output_file, 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        out_file.write(chunk)
        except requests.exceptions.ConnectionError as e:
            print(f"Connector Error: Could not download large file: {e}")
        except requests.exceptions.Timeout as e:
            print(f"Network Error: Request Timed Out, Check Connection: {e}")
        except requests.exceptions.RequestException as e:
            print(f"A catastrophic failure occured when trying to download the file: {e}")
        except OSError as e:
            print(f"OS Exception: {e}")
        else:
            print(f"Successfully downloaded {url} --> {output_file}")
            return True
        return False


    def get_latest_release_metadata(self) -> dict:
        """
            Downloads latest release metadata from Plex
            In the future, will support beta release channels
            but I don't use those.
        """

        url = self.configs['source']
        output_file = '/tmp/plex_versions.json'

        # Load variables is friendly format from
        # configs
        platform = self.configs['os']
        arch = f"{platform.lower()}-{self.configs['arch']}"
        distro = self.configs['packaging']

        if self.download_file(url, output_file):
            try:
                with open(output_file, 'r', encoding='UTF-8') as file:
                    releases = json.load(file)
            except FileNotFoundError as e:
                print(f"Error loading releases JSON: {e}")
            else:
                version = releases['computer'][platform]['version']
                metadata = [
                    r for r in releases['computer'][platform]['releases']
                    if r['build'] == arch and r['distro'] == distro
                ]
                return version, metadata

    def get_installed_version(self) -> str:
        """
            Gets the current installed version
        """
        if self.configs['os'] == 'Linux':
            if self.configs['packaging'] == 'debian':
                args = [ 'dpkg', '-s', 'plexmediaserver']
                output = subprocess.run(args, capture_output=True, text=True, check=False)
                ver_re = r'.*Version:\s*(\d\.\d+\.\d+\.\d+-\w+).*'
                match = re.match(ver_re, output.stdout, flags=re.MULTILINE|re.DOTALL|re.IGNORECASE)
                if match:
                    return match.group(1)
                else:
                    print("No match")
            else:
                print("Currently not supporting other OS/Distro types")
        else:
            print("Currently not supporting other OS/Distro types")

    def calculate_sha1(self, input_file: str) -> str:
        """
            Calculates the sha1 of the file we downloaded
            to verify authenticity before installing
        """
        calc = hashlib.new('sha1')
        try:
            with open(input_file, 'rb') as in_file:
                for chunk in iter(lambda: in_file.read(4096), b''):
                    calc.update(chunk)
        except OSError as e:
            print(f"OS Error while calculating SHA1: {e}")
        else:
            return calc.hexdigest()
        return "Failed to calculate"


    def install_update(self, update_path: str, update_version: str) -> bool:
        """
            Backups up Preferences.xml, gracefullyy stops services, 
            installs the updates,and restarts services.
        """

        source_file = '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Preferences.xml'
        backup_file = f"/tmp/plex-preferences-backup-{update_version}.xml"

        backup_args = [
            'cp',
            source_file,
            backup_file
        ]

        # Backup Preferences.xml
        subprocess.run(backup_args, capture_output=False, check=False)

        # Stop Plex
        subprocess.run(
            [
                'systemctl',
                'stop',
                'plexmediaserver'
            ],
            capture_output=False,
            check=False
        )

        # Update Plex
        subprocess.run(
            [
                'dpkg',
                '-i',
                update_path
            ],
            capture_output=False,
            check=False
        )

        # Start Plex
        subprocess.run(
            [
                'systemctl',
                'start',
                'plexmediaserver'
            ],
            capture_output=False,
            check=False
        )

        # Check Plex Status
        output = subprocess.run(
            [
                'systemctl',
                'status',
                'plexmediaserver'
            ],
            capture_output=True,
            text=True,
            check=False
        )

        status_re = r'.*Active:\s*(?P<State>\w+)\s*(?P<Details>\(\w+\)).*'
        match = re.match(status_re, output.stdout, flags=re.MULTILINE|re.DOTALL|re.IGNORECASE)
        if match:
            if match.group('State') == 'active':
                print('Successfully updated Plex! Enjoy your ISOs!')
                return True
            else:
                print('Updated Plex, but something went wrong. Intervention needed.')
                print("Showing 'systemctl status plexmediaserver': ")
                print(output.stdout)
        return False

if __name__ == '__main__':
    updater = PlexAutoUpdater(config_path='/opt/scripts/pyupdater-plex/config.yml')
    newest_release = updater.get_latest_release_metadata()
    current_version = updater.get_installed_version()
    if current_version != newest_release[0]:
        print(f"Updating from {current_version} --> {newest_release[0]}")
        download_url = newest_release[1][0]['url']
        download_path = f"/tmp/plex-{newest_release[0]}.deb"
        download_status = updater.download_large_file( url=download_url, output_file=download_path)
        if download_status:
            sha1 = updater.calculate_sha1(input_file=download_path)
            if sha1 == newest_release[1][0]['checksum']:
                updater.install_update(download_path, newest_release[0])
            else:
                print('FATAL: Skipping update, downloaded file checksum does not match.')
                print(f"EXPECTED: {newest_release[1][0]['checksum']}")
                print(f"GOT: {sha1}")
    else:
        print("Nothing to do, you're on the latest version!")
