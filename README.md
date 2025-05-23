# Perseus CLI

A command-line interface for the Perseus APK version management system.

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Make the CLI executable:
```bash
chmod +x perseus_cli.py
```

## Usage

### Push an APK
```bash
./perseus_cli.py push path/to/your.apk
```

### Pull APKs

Pull latest frozen version of all APKs:
```bash
./perseus_cli.py pull
```

Pull specific version of all APKs:
```bash
./perseus_cli.py pull --version v1.0.0
```

Pull specific app (latest version):
```bash
./perseus_cli.py pull app_name
```

Pull specific app and version:
```bash
./perseus_cli.py pull app_name v1.0.0
```

### Freeze a Version
```bash
./perseus_cli.py freeze v1.0.0
```

## Configuration

By default, the CLI connects to `http://localhost:5000`. To use a different server, modify the `base_url` in the `PerseusClient` class initialization.
