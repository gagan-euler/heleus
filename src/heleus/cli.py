"""Command line interface for Heleus."""

import sys
import json
import argparse
from typing import Optional, List
from datetime import datetime
from tabulate import tabulate

from heleus.client import PerseusClient
from heleus.config import ConfigManager

# Use solid lines for all tables
TABLE_FORMAT = "simple_grid"

def create_parser() -> argparse.ArgumentParser:
    """Create the command line parser.

    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(description="Heleus - APK Version Management Tool")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Server configuration commands
    config_parser = subparsers.add_parser('config', help='Configure Heleus')
    config_subparsers = config_parser.add_subparsers(dest='config_command', help='Configuration commands')
    
    # Set server command
    set_server_parser = config_subparsers.add_parser('server', help='Set server configuration')
    set_server_parser.add_argument('host', help='Server hostname or IP')
    set_server_parser.add_argument('port', type=int, help='Server port')

    # Show server command
    config_subparsers.add_parser('show', help='Show current configuration')

    # List commands
    list_parser = subparsers.add_parser('list', help='List versions and apps')
    list_subparsers = list_parser.add_subparsers(dest='list_command', help='List commands')
    
    # List versions command
    list_subparsers.add_parser('versions', help='List all frozen versions')
    
    # List apps command
    list_subparsers.add_parser('apps', help='List all apps with their latest versions')
    
    # List all app versions command
    list_subparsers.add_parser('all', help='List all apps with all their versions')

    # Push command
    push_parser = subparsers.add_parser('push', help='Push an APK to the repository')
    push_parser.add_argument('apk_path', help='Path to the APK file')

    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Pull APK(s) from the repository')
    pull_parser.add_argument('app_name', nargs='?', help='Name of the app to pull')
    pull_parser.add_argument('version', nargs='?', default='latest', help='Version to pull (defaults to latest)')

    # Freeze command
    freeze_parser = subparsers.add_parser('freeze', help='Freeze a version')
    freeze_parser.add_argument('version', help='Version name to freeze')

    return parser


def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display.

    Args:
        timestamp: ISO format timestamp

    Returns:
        str: Formatted timestamp
    """
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, AttributeError):
        return timestamp


def handle_list_command(args: argparse.Namespace) -> int:
    """Handle list commands.

    Args:
        args: Parsed command line arguments

    Returns:
        int: Exit code
    """
    client = PerseusClient()

    if args.list_command == 'versions':
        success, result = client.list_versions()
        if success:
            versions = result.get('versions', [])
            if not versions:
                print("No frozen versions found.")
                return 0
            
            # Prepare table data
            headers = ["Version", "Created At"]
            table_data = [
                [version['version'], format_timestamp(version['created_at'])]
                for version in versions
            ]
            
            print("\nFrozen Versions:")
            print(tabulate(table_data, headers=headers, tablefmt=TABLE_FORMAT))
            return 0

    elif args.list_command == 'apps':
        success, result = client.list_apps()
        if success:
            apps = result.get('apps', [])
            if not apps:
                print("No apps found.")
                return 0
            
            # Prepare table data
            headers = ["App Name", "Latest Hash", "Last Updated", "Version Tag"]
            table_data = [
                [
                    app['name'],
                    app['latest_hash'][:12] + "...",  # Show first 12 chars of hash
                    format_timestamp(app['last_updated']),
                    app['version_tag'] or "N/A"
                ]
                for app in apps
            ]
            
            print("\nApps (Latest Versions):")
            print(tabulate(table_data, headers=headers, tablefmt=TABLE_FORMAT))
            return 0

    elif args.list_command == 'all':
        success, result = client.list_all_app_versions()
        if success:
            apps = result.get('apps', [])
            if not apps:
                print("No apps found.")
                return 0
            
            print("\nAll App Versions:")
            for app in apps:
                print(f"\n{app['name']}:")
                
                # Prepare table data for this app's versions
                headers = ["Hash", "Timestamp", "Message", "Version Tag"]
                table_data = [
                    [
                        version['hash'][:12] + "...",  # Show first 12 chars of hash
                        format_timestamp(version['timestamp']),
                        version['message'] or "N/A",
                        version['version_tag'] or "N/A"
                    ]
                    for version in app['versions']
                ]
                
                print(tabulate(table_data, headers=headers, tablefmt=TABLE_FORMAT))
            return 0

    else:
        print("Error: Invalid list command")
        return 1

    print(f"Error: {result.get('error', 'Unknown error occurred')}")
    return 1


def handle_config_command(args: argparse.Namespace) -> int:
    """Handle configuration commands.

    Args:
        args: Parsed command line arguments

    Returns:
        int: Exit code
    """
    config = ConfigManager()

    if args.config_command == 'server':
        config.set_server(args.host, args.port)
        print(f"Server configuration updated: http://{args.host}:{args.port}")
        return 0
    elif args.config_command == 'show':
        server_info = config.get_server_info()
        headers = ["Setting", "Value"]
        table_data = [
            ["Server URL", f"http://{server_info['host']}:{server_info['port']}"]
        ]
        print("\nCurrent Configuration:")
        print(tabulate(table_data, headers=headers, tablefmt=TABLE_FORMAT))
        return 0
    else:
        print("Error: Invalid config command")
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: List of command line arguments

    Returns:
        int: Exit code
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    if args.command == 'config':
        return handle_config_command(args)
    elif args.command == 'list':
        return handle_list_command(args)

    client = PerseusClient()

    # Check if server is running
    if not client.check_server_status():
        print("Error: Cannot connect to Perseus server")
        return 1

    success = False
    result = {}

    if args.command == 'push':
        success, result = client.push(args.apk_path)
    elif args.command == 'pull':
        success, result = client.pull(args.app_name, args.version)
    elif args.command == 'freeze':
        success, result = client.freeze(args.version)

    if success:
        if 'message' in result:
            print(result['message'])
        elif 'status' in result:
            print(result['status'])
        else:
            print("Operation completed successfully")
    else:
        print(f"Error: {result.get('error', 'Unknown error occurred')}")

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main()) 