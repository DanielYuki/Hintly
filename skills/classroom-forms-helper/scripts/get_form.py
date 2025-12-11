#!/usr/bin/env python3
"""
Get Google Form structure from Classroom activity.

Reads form questions and displays them in a readable format.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import argparse
import json

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from core.browser_forms import BrowserFormsClient


console = Console()


def get_form(form_url: str, output_format: str = "table"):
    """
    Get and display Google Form structure.
    
    Args:
        form_url: Google Form URL
        output_format: Output format ('table' or 'json')
    """
    console.print(f"[cyan]Fetching form from URL...[/cyan]")
    
    client = BrowserFormsClient()
    form = client.get_form(form_url)
    
    console.print(f"[green]✓[/green] Form: [bold]{form.title}[/bold]")
    console.print(f"[green]✓[/green] Questions: [cyan]{len(form.questions)}[/cyan]")
    
    if output_format == "json":
        # JSON output
        output = {
            "id": form.id,
            "title": form.title,
            "description": form.description,
            "question_count": len(form.questions),
            "questions": [
                {
                    "id": q.id,
                    "title": q.title,
                    "type": q.type,
                    "required": q.required,
                    "options": q.options if q.options else [],
                    "description": q.description
                }
                for q in form.questions
            ]
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        # Table output
        if form.description:
            console.print(f"\n[dim]{form.description}[/dim]\n")
        
        table = Table(title=f"Form Questions ({len(form.questions)})")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Question", style="white")
        table.add_column("Type", style="yellow", width=15)
        table.add_column("Required", style="red", width=8)
        table.add_column("Options", style="green")
        
        for i, question in enumerate(form.questions, 1):
            options_str = ""
            if question.options:
                options_str = f"{len(question.options)} choices"
            
            required_str = "✓" if question.required else ""
            
            table.add_row(
                str(i),
                question.title,
                question.type,
                required_str,
                options_str
            )
        
        console.print(table)
        
        console.print(f"\n[dim]Form URL: {form_url}[/dim]")


def main():
    parser = argparse.ArgumentParser(
        description="Get Google Form structure"
    )
    parser.add_argument(
        "form_url",
        help="Google Form URL"
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)"
    )
    
    args = parser.parse_args()
    
    try:
        get_form(args.form_url, args.format)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
