#!/usr/bin/env python3
"""
Generate answer template from Google Form.

Creates markdown template with all questions for study/preparation.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import argparse
from datetime import datetime

from rich.console import Console

from core.browser_forms import BrowserFormsClient
from core.config import get_config


console = Console()


def generate_template(form_url: str, output_path: str = None):
    """
    Generate answer template from form.
    
    Args:
        form_url: Google Form URL
        output_path: Optional output path
    """
    config = get_config()
    
    # Get form
    console.print("[cyan]Fetching form...[/cyan]")
    client = BrowserFormsClient()
    form = client.get_form(form_url)
    
    console.print(f"[green]✓[/green] Form: [bold]{form.title}[/bold]")
    
    # Generate template
    template = f"# {form.title}\n\n"
    template += f"**Date**: {datetime.now().strftime('%Y-%m-%d')}\n"
    template += f"**Questions**: {len(form.questions)}\n\n"
    
    if form.description:
        template += f"{form.description}\n\n"
    
    template += "---\n\n"
    
    for i, question in enumerate(form.questions, 1):
        template += f"## Question {i}\n\n"
        template += f"**{question.title}**\n\n"
        
        if question.description:
            template += f"*{question.description}*\n\n"
        
        template += f"**Type**: {question.type}\n"
        template += f"**Required**: {'Yes' if question.required else 'No'}\n\n"
        
        if question.options:
            template += "**Options**:\n"
            for opt in question.options:
                template += f"- [ ] {opt}\n"
            template += "\n"
        
        template += "**Your Answer**:\n\n"
        template += "```\n\n\n```\n\n"
        template += "---\n\n"
    
    # Save template
    if output_path:
        output = Path(output_path)
    else:
        # Use reports directory (not solutions - templates are study aids, not solutions)
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in form.title)
        filename = f"{safe_title}_template.md"
        output = config.reports_dir / filename
    
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template, encoding='utf-8')
    
    console.print(f"\n[green]✓ Template generated![/green]")
    console.print(f"Saved to: [cyan]{output}[/cyan]")
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate answer template from Google Form"
    )
    parser.add_argument(
        "form_url",
        help="Google Form URL"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output path for template"
    )
    
    args = parser.parse_args()
    
    try:
        generate_template(args.form_url, args.output)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
