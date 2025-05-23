"""Perseus client implementation."""

import os
import io
import zipfile
import requests
from typing import Optional, Tuple, Dict, Any, List
from tqdm import tqdm

from heleus.config import ConfigManager


class PerseusClient:
    """Client for interacting with Perseus APK management server."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize Perseus client.

        Args:
            base_url: Optional base URL of the Perseus server. If not provided,
                     will use the URL from config.
        """
        self.config = ConfigManager()
        self.base_url = base_url.rstrip('/') if base_url else self.config.get_server_url()

    def check_server_status(self) -> bool:
        """Check if the Perseus server is running.

        Returns:
            bool: True if server is running, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/v1/status")
            return response.status_code == 200
        except requests.RequestException:
            return False

    def push(self, apk_path: str) -> Tuple[bool, Dict[str, Any]]:
        """Push an APK to the repository.

        Args:
            apk_path: Path to the APK file

        Returns:
            Tuple[bool, Dict[str, Any]]: Success status and response data
        """
        if not os.path.exists(apk_path):
            return False, {"error": f"APK file '{apk_path}' not found"}

        if not apk_path.lower().endswith('.apk'):
            return False, {"error": "File must be an APK"}

        try:
            # Get file size for progress bar
            file_size = os.path.getsize(apk_path)
            
            with open(apk_path, 'rb') as f:
                # Create a wrapper for the file that includes a progress bar
                with tqdm(
                    total=file_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"Uploading {os.path.basename(apk_path)}"
                ) as pbar:
                    # Create a custom file-like object that updates the progress bar
                    class ProgressFile:
                        def __init__(self, file, pbar):
                            self.file = file
                            self.pbar = pbar
                        
                        def read(self, size=-1):
                            """Read from the file and update the progress bar.
                            
                            Args:
                                size: Number of bytes to read. -1 means read all.
                            """
                            if size == -1:
                                data = self.file.read()
                            else:
                                data = self.file.read(size)
                            self.pbar.update(len(data))
                            return data

                    files = {
                        'file': (
                            os.path.basename(apk_path),
                            ProgressFile(f, pbar),
                            'application/vnd.android.package-archive'
                        )
                    }
                    response = requests.post(
                        f"{self.base_url}/api/v1/push",
                        files=files
                    )

            if response.status_code == 200:
                return True, response.json()
            return False, {"error": response.json().get('error', 'Unknown error')}

        except requests.RequestException as e:
            return False, {"error": f"Error pushing APK: {str(e)}"}

    def pull(self, app_name: Optional[str] = None, version: str = "latest") -> Tuple[bool, Dict[str, Any]]:
        """Pull APK(s) from the repository.

        Args:
            app_name: Optional name of specific app to pull
            version: Version to pull (defaults to latest)

        Returns:
            Tuple[bool, Dict[str, Any]]: Success status and response data
        """
        try:
            if app_name:
                # Pull specific APK
                response = requests.get(
                    f"{self.base_url}/api/v1/pull/{version}/{app_name}",
                    stream=True
                )
                if response.status_code == 200:
                    os.makedirs(app_name, exist_ok=True)
                    output_path = os.path.join(app_name, f"{app_name}.apk")
                    
                    # Get the total file size from headers
                    total_size = int(response.headers.get('content-length', 0))

                    with open(output_path, 'wb') as f:
                        with tqdm(
                            total=total_size,
                            unit='B',
                            unit_scale=True,
                            unit_divisor=1024,
                            desc=f"Downloading {app_name}.apk"
                        ) as pbar:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    pbar.update(len(chunk))
                    return True, {"message": f"Successfully downloaded to {output_path}"}
            else:
                # Pull all APKs for version
                url = f"{self.base_url}/api/v1/pull/{version}" if version != "latest" else f"{self.base_url}/api/v1/pull"
                response = requests.get(url, stream=True)
                
                if response.status_code == 200:
                    # Get the total file size from headers
                    total_size = int(response.headers.get('content-length', 0))
                    
                    # Download with progress bar
                    zip_data = io.BytesIO()
                    with tqdm(
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=f"Downloading version {version}"
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                zip_data.write(chunk)
                                pbar.update(len(chunk))
                    
                    zip_data.seek(0)
                    print("\nExtracting files...")
                    with zipfile.ZipFile(zip_data) as zip_ref:
                        # Get total number of files for extraction progress
                        total_files = len(zip_ref.filelist)
                        with tqdm(
                            total=total_files,
                            unit='files',
                            desc="Extracting"
                        ) as pbar:
                            for file in zip_ref.filelist:
                                zip_ref.extract(file)
                                pbar.update(1)
                    
                    return True, {"message": f"Successfully downloaded and extracted version {version}"}

            if response.status_code != 200:
                return False, {"error": response.json().get('error', 'Unknown error')}

        except requests.RequestException as e:
            return False, {"error": f"Error pulling APK(s): {str(e)}"}

        return False, {"error": "Unknown error occurred"}

    def freeze(self, version: str) -> Tuple[bool, Dict[str, Any]]:
        """Freeze a version.

        Args:
            version: Version name to freeze

        Returns:
            Tuple[bool, Dict[str, Any]]: Success status and response data
        """
        try:
            response = requests.get(f"{self.base_url}/api/v1/freeze/{version}")
            if response.status_code == 200:
                return True, response.json()
            return False, {"error": response.json().get('error', 'Unknown error')}
        except requests.RequestException as e:
            return False, {"error": f"Error freezing version: {str(e)}"}

    def list_versions(self) -> Tuple[bool, Dict[str, Any]]:
        """List all frozen versions.

        Returns:
            Tuple[bool, Dict[str, Any]]: Success status and list of versions
        """
        try:
            response = requests.get(f"{self.base_url}/api/v1/versions")
            if response.status_code == 200:
                return True, response.json()
            return False, {"error": response.json().get('error', 'Unknown error')}
        except requests.RequestException as e:
            return False, {"error": f"Error listing versions: {str(e)}"}

    def list_apps(self) -> Tuple[bool, Dict[str, Any]]:
        """List all apps with their latest hashes and version tags.

        Returns:
            Tuple[bool, Dict[str, Any]]: Success status and list of apps
        """
        try:
            response = requests.get(f"{self.base_url}/api/v1/apps")
            if response.status_code == 200:
                return True, response.json()
            return False, {"error": response.json().get('error', 'Unknown error')}
        except requests.RequestException as e:
            return False, {"error": f"Error listing apps: {str(e)}"}

    def list_all_app_versions(self) -> Tuple[bool, Dict[str, Any]]:
        """List all apps with all their versions.

        Returns:
            Tuple[bool, Dict[str, Any]]: Success status and detailed app list
        """
        try:
            response = requests.get(f"{self.base_url}/api/v1/apps/all")
            if response.status_code == 200:
                return True, response.json()
            return False, {"error": response.json().get('error', 'Unknown error')}
        except requests.RequestException as e:
            return False, {"error": f"Error listing app versions: {str(e)}"} 