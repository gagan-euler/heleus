# Heleus

A command-line interface for Perseus APK version management system. Heleus provides a simple way to manage APK versions, similar to how Git manages source code versions.

## Features

- Push APKs to the repository with progress tracking
- Pull specific APKs or entire version bundles
- Freeze versions for release
- Configure server settings
- Progress bars for all file operations
- Persistent server configuration

## Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/heleus.git
cd heleus

# Install using Poetry
poetry install

# Run commands through Poetry
poetry run heleus --help

# Or activate the Poetry shell and run directly
poetry shell
heleus --help
```

### Using pip

```bash
pip install heleus
```

## Configuration

Heleus stores its configuration in `~/.heleus/config.json`. You can configure the server settings using the CLI:

```bash
# Set server configuration
heleus config server <host> <port>

# View current configuration
heleus config show
```

## Usage

### Push an APK

Upload an APK to the repository:

```bash
heleus push path/to/your.apk
```

The command shows a progress bar during upload and returns the upload status.

### Pull APKs

Pull the latest frozen version of all APKs:
```bash
heleus pull
```

Pull a specific version of all APKs:
```bash
heleus pull --version v1.0.0
```

Pull a specific app (latest version):
```bash
heleus pull app_name
```

Pull a specific app and version:
```bash
heleus pull app_name v1.0.0
```

All pull operations show progress bars for download and extraction.

### Freeze a Version

Create a frozen version for release:
```bash
heleus freeze v1.0.0
```

## Command Reference

```
heleus
  config
    server <host> <port>  Configure server connection
    show                  Display current configuration
  push <apk_path>        Upload an APK
  pull [app] [version]   Download APK(s)
  freeze <version>       Create a frozen version
```

## Development

To contribute to Heleus:

1. Fork the repository
2. Create a feature branch
3. Install development dependencies:
   ```bash
   poetry install
   ```
4. Make your changes
5. Run tests:
   ```bash
   poetry run pytest
   ```
6. Submit a pull request

## License

MIT License
