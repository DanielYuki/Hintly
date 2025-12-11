#!/usr/bin/env python3
"""
One-time browser login for Google Forms access.

This script opens a browser window where you can log in to Google.
The session is saved and reused for automated form scraping.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from playwright.sync_api import sync_playwright
from rich.console import Console
from rich.panel import Panel

console = Console()


def setup_browser_login():
    """
    Open browser for one-time Google login.
    
    The browser session will be saved and reused for automated scraping.
    """
    console.print("[cyan]Setting up browser login for Google Forms...[/cyan]\n")
    
    user_data_dir = Path.home() / ".hintly" / "browser_data"
    user_data_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(Panel.fit(
        "[yellow]A browser window will open.[/yellow]\n\n"
        "1. Log in to your Google account\n"
        "2. Navigate to any Google Form to verify access\n"
        "3. Close the browser when done\n\n"
        "Your session will be saved for future use.",
        title="Browser Login",
        border_style="yellow"
    ))
    
    input("\nPress Enter to open browser...")
    
    with sync_playwright() as p:
        # Launch browser with persistent context (saves session)
        browser = p.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=False,  # Show browser
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = browser.new_page()
        page.goto("https://accounts.google.com/")
        
        console.print("\n[green]Browser opened![/green]")
        console.print("[dim]Log in to Google and test a form if you like.[/dim]")
        console.print("[dim]Close the browser window when done.[/dim]\n")
        
        # Wait for user to close browser
        try:
            page.wait_for_event("close", timeout=0)  # Wait indefinitely
        except:
            pass
        
        browser.close()
    
    console.print(Panel.fit(
        "[green]✓ Browser session saved![/green]\n\n"
        "You can now use the forms scripts without manual login.",
        title="Setup Complete",
        border_style="green"
    ))


def main():
    try:
        setup_browser_login()
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
