#!/usr/bin/env python3
"""
Solve Google Form questions using AI.

Extracts questions and uses LLM to generate thoughtful answers.
Saves completed form to solutions folder.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import argparse
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.browser_forms import BrowserFormsClient
from core.llm_client import LLMClient, LLMProvider
from core.config import get_config


console = Console()


def solve_form(form_url: str, provider: str = None, context: str = ""):
    """
    Solve form questions using AI.
    
    Args:
        form_url: Google Form URL
        provider: LLM provider override
        context: Additional context for answering (e.g., "Based on Cold War history")
    """
    config = get_config()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Get form
        task = progress.add_task("Fetching form...", total=None)
        client = BrowserFormsClient()
        form = client.get_form(form_url)
        progress.update(task, description=f"✓ Form: {form.title}")
        progress.stop_task(task)
        
        console.print(f"[green]✓[/green] Questions: [cyan]{len(form.questions)}[/cyan]\n")
        
        # Initialize LLM
        if provider:
            llm_client = LLMClient(LLMProvider(provider))
        else:
            llm_client = LLMClient()
        
        # Build solution document
        solution = f"# {form.title} - Solutions\n\n"
        solution += f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        solution += f"**Questions**: {len(form.questions)}\n"
        solution += f"**Solved by**: AI ({llm_client.provider.value})\n\n"
        
        if form.description:
            solution += f"**Form Description**: {form.description}\n\n"
        
        if context:
            solution += f"**Context**: {context}\n\n"
        
        solution += "---\n\n"
        
        # Answer each question
        for i, question in enumerate(form.questions, 1):
            task = progress.add_task(f"Answering question {i}/{len(form.questions)}...", total=None)
            
            # Get AI answer using the LLM client's interface
            full_question = f"{question.title}\n\n"
            if question.description:
                full_question += f"{question.description}\n\n"
            if question.options:
                full_question += "Options:\n" + "\n".join(f"- {opt}" for opt in question.options) + "\n\n"
            
            # Build instruction based on question type
            if question.type == "MULTIPLE_CHOICE" and question.options:
                instruction = "Select the most appropriate option and explain your reasoning briefly."
            elif question.type == "SHORT_ANSWER":
                instruction = "Provide a concise answer (1-2 sentences)."
            elif question.type == "PARAGRAPH":
                instruction = "Provide a detailed answer (2-4 paragraphs)."
            else:
                instruction = "Provide an appropriate answer."
            
            # Use summarize method with custom prompt
            answer = llm_client.summarize(
                full_question,
                prompt=instruction,
                context=context if context else f"Form: {form.title}"
            )
            
            # Add to solution
            solution += f"## Question {i}\n\n"
            solution += f"**{question.title}**\n\n"
            
            if question.description:
                solution += f"*{question.description}*\n\n"
            
            if question.options:
                solution += "**Options**:\n"
                for opt in question.options:
                    solution += f"- {opt}\n"
                solution += "\n"
            
            solution += f"**Answer**:\n\n{answer}\n\n"
            solution += "---\n\n"
            
            progress.update(task, description=f"✓ Question {i} answered")
            progress.stop_task(task)
    
    # Save solution
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in form.title)
    filename = f"{safe_title}_solution.md"
    output_path = config.solutions_dir / filename
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(solution, encoding='utf-8')
    
    console.print(f"\n[green]✓ Form solved![/green]")
    console.print(f"Saved to: [cyan]{output_path}[/cyan]\n")
    
    # Show preview
    console.print("[bold]Solution Preview:[/bold]\n")
    lines = solution.split('\n')
    preview = '\n'.join(lines[:30])
    console.print(preview)
    if len(lines) > 30:
        console.print("\n[dim]... (truncated, see file for full solution)[/dim]")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Solve Google Form questions using AI"
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
    parser.add_argument(
        "--context",
        "-c",
        default="",
        help="Additional context for answering (e.g., 'Based on Cold War history')"
    )
    
    args = parser.parse_args()
    
    try:
        solve_form(args.form_url, args.provider, args.context)
    except KeyboardInterrupt:
        console.print("\n[yellow]Solving cancelled[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
