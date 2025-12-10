#!/usr/bin/env python3
"""
Authentication script for Google Classroom.

Usage:
    python auth.py --check       Check authentication status
    python auth.py --setup       Start OAuth2 flow
    python auth.py --revoke      Revoke and clear credentials
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from rich.console import Console
from rich.panel import Panel

from core.auth import OAuth2Flow, get_auth_status
from core.config import get_config


console = Console()


def check_auth():
    """Check current authentication status."""
    status = get_auth_status()

    if status["authenticated"]:
        console.print(Panel(
            f"[green]✓ Authenticated[/green]\n\nToken stored at: {status['token_path']}",
            title="Authentication Status",
            border_style="green",
        ))
        return True
    else:
        console.print(Panel(
            "[yellow]✗ Not authenticated[/yellow]\n\n"
            "Run with --setup to authenticate.",
            title="Authentication Status",
            border_style="yellow",
        ))
        return False


def setup_auth():
    """Start OAuth2 authentication flow."""
    console.print("[bold]Starting Google Classroom authentication...[/bold]\n")

    flow = OAuth2Flow()

    # Check if already authenticated
    if flow.check_auth():
        console.print("[green]Already authenticated![/green]")
        return True

    # Try local server flow (opens browser automatically)
    console.print("Opening browser for Google login...\n")

    try:
        if flow.run_local_server():
            console.print(Panel(
                "[green]✓ Authentication successful![/green]\n\n"
                f"Token saved to: {flow.token_path}",
                title="Success",
                border_style="green",
            ))
            return True
        else:
            console.print("[red]Authentication failed.[/red]")
            return False

    except Exception as e:
        # If local server fails, provide manual URL
        console.print(f"[yellow]Browser flow failed: {e}[/yellow]\n")
        console.print("Generating login URL for manual authentication...\n")

        login_url = flow.get_login_url()
        console.print(Panel(
            f"[bold]Please visit this URL to authenticate:[/bold]\n\n{login_url}\n\n"
            "After authorizing, copy the code and run:\n"
            "  python auth.py --code YOUR_CODE",
            title="Manual Authentication",
            border_style="blue",
        ))
        return False


def revoke_auth():
    """Revoke and clear stored credentials."""
    flow = OAuth2Flow()

    if flow.revoke():
        console.print(Panel(
            "[green]✓ Credentials revoked and cleared.[/green]",
            title="Revoked",
            border_style="green",
        ))
        return True

    return False


def authenticate_with_code(code: str):
    """Complete authentication with authorization code."""
    flow = OAuth2Flow()

    if flow.authenticate_with_code(code):
        console.print(Panel(
            "[green]✓ Authentication successful![/green]\n\n"
            f"Token saved to: {flow.token_path}",
            title="Success",
            border_style="green",
        ))
        return True
    else:
        console.print("[red]Failed to authenticate with provided code.[/red]")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Manage Google Classroom authentication"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check current authentication status",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Start OAuth2 authentication flow",
    )
    parser.add_argument(
        "--revoke",
        action="store_true",
        help="Revoke and clear stored credentials",
    )
    parser.add_argument(
        "--code",
        type=str,
        help="Authorization code for manual authentication",
    )

    args = parser.parse_args()

    # Validate config
    config = get_config()
    if not args.check:  # Only validate on setup
        errors = config.validate()
        if errors and "--setup" in sys.argv:
            console.print("[red]Configuration errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            console.print("\nPlease set up your .env file with required credentials.")
            sys.exit(1)

    # Execute command
    if args.check:
        success = check_auth()
    elif args.setup:
        success = setup_auth()
    elif args.revoke:
        success = revoke_auth()
    elif args.code:
        success = authenticate_with_code(args.code)
    else:
        parser.print_help()
        success = True

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
