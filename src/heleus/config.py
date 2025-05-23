"""Configuration management for Heleus."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

DEFAULT_CONFIG = {
    "server": {
        "host": "localhost",
        "port": 5000
    }
}

class ConfigManager:
    """Manages Heleus configuration."""

    def __init__(self):
        """Initialize the configuration manager."""
        self.config_dir = Path.home() / ".heleus"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_exists()

    def _ensure_config_exists(self) -> None:
        """Ensure the config directory and file exist."""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self.save_config(DEFAULT_CONFIG)

    def load_config(self) -> Dict[str, Any]:
        """Load the configuration from file.

        Returns:
            Dict[str, Any]: The configuration dictionary
        """
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return DEFAULT_CONFIG

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save the configuration to file.

        Args:
            config: The configuration dictionary to save
        """
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    def get_server_url(self) -> str:
        """Get the server URL from config.

        Returns:
            str: The complete server URL
        """
        config = self.load_config()
        host = config["server"]["host"]
        port = config["server"]["port"]
        return f"http://{host}:{port}"

    def set_server(self, host: str, port: int) -> None:
        """Set the server configuration.

        Args:
            host: Server hostname or IP
            port: Server port number
        """
        config = self.load_config()
        config["server"] = {
            "host": host,
            "port": port
        }
        self.save_config(config)

    def get_server_info(self) -> Dict[str, Any]:
        """Get the server configuration.

        Returns:
            Dict[str, Any]: Server configuration dictionary
        """
        config = self.load_config()
        return config["server"] 