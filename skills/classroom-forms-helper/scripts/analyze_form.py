#!/usr/bin/env python3
"""
Analyze Google Form questions using LLM.

Categorizes questions and provides study suggestions.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import argparse

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from core.forms_api import FormsClient
from core.llm_client import LLMClient, LLMProvider


console = Console()


def analyze_form(form_url: str, provider: str = None):
    """
    Analyze form questions using LLM.
    
    Args:
        form_url: Google Form URL
        provider: LLM provider override
    """
    # Get form
    console.print("[cyan]Fetching form...[/cyan]")
    client = FormsClient()
    form = client.get_form_from_url(form_url)
    
    console.print(f"[green]✓[/green] Form: [bold]{form.title}[/bold]")
    console.print(f"[green]✓[/green] Questions: [cyan]{len(form.questions)}[/cyan]")
    
    # Prepare questions for analysis
    questions_list = [f"{i+1}. {q.title} ({q.type})" for i, q in enumerate(form.questions)]
    
    # Analyze with LLM
    console.print("\n[cyan]Analyzing questions with AI...[/cyan]")
    
    if provider:
        llm_client = LLMClient(LLMProvider(provider))
    else:
        llm_client = LLMClient()
    
    context = f"Form: {form.title}"
    if form.description:
        context += f" | {form.description}"
    
    result = llm_client.analyze_questions(questions_list, context=context)
    
    # Display results
    console.print("\n" + "="*60)
    md = Markdown(result["analysis"])
    console.print(md)
    console.print("="*60)
    
    console.print(f"\n[dim]Analyzed by: {result['provider']}[/dim]")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Google Form questions with AI"
    )
    parser.add_argument(
        "form_url",
        help="Google Form URL"
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai"],
        help="LLM provider override"
    )
    
    args = parser.parse_args()
    
    try:
        analyze_form(args.form_url, args.provider)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:{e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
