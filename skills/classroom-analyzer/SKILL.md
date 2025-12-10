---
name: classroom-analyzer
description: >
  Analyzes and summarizes Google Classroom content. Generates PDF reports,
  Markdown summaries, and JSON exports for materials and coursework.
  Use when the user wants to analyze, summarize, report on, or export
  educational content. Triggers: "summarize this material", "create a report",
  "analyze the course content", "export data", "give me a summary",
  "generate a PDF", "explain this material".
---

# Classroom Analyzer

Analyze and summarize Google Classroom content with multiple output formats.

## Capabilities

- Generate **PDF reports** for course materials
- Create **Markdown summaries** for quick reading
- **Export JSON** data for further processing
- Summarize entire courses with statistics

## Prerequisites

- User must be authenticated (use `classroom-explorer` skill if needed)
- Need course ID and item ID (use `classroom-explorer` to list them)

## Commands

### Analyze Material

Generate a comprehensive analysis of a specific material:

```bash
python {baseDir}/scripts/analyze_material.py --course-id <ID> --material-id <ID>
```

Options:

- `--format pdf|markdown|json` - Output format (default: markdown)
- `--include-analysis` - Add AI-generated insights
- `--output <PATH>` - Custom output path

### Summarize Course

Generate an overview of an entire course:

```bash
python {baseDir}/scripts/summarize_course.py --course-id <ID>
```

Options:

- `--format pdf|markdown` - Output format (default: markdown)
- `--include-stats` - Include statistics (default: true)

### Export Data

Export course data to JSON for further processing:

```bash
python {baseDir}/scripts/export_data.py --course-id <ID>
```

Options:

- `--include-coursework` - Include coursework items
- `--include-materials` - Include materials
- `--include-announcements` - Include announcements
- `--all` - Include everything

## Workflow

1. **Identify content**: Use `classroom-explorer` to find item IDs
2. **Choose output format**: PDF for formal reports, Markdown for quick reading
3. **Generate output**: Run appropriate script
4. **Review result**: Output saved to `outputs/reports/` or `outputs/exports/`

## Output Examples

### Markdown Summary

```markdown
# Material: Chapter 5 Study Guide

**Course**: Mathematics 101
**Created**: 2024-12-01

## Summary
This material covers key concepts from Chapter 5...

## Key Topics
- Derivatives
- Chain Rule
- ...
```

### PDF Report

Professional PDF with:

- Title and metadata
- Description section
- AI-generated analysis
- Attached resources table
- Clean formatting

## Output Locations

| Format | Directory |
|--------|-----------|
| PDF | `outputs/reports/*.pdf` |
| Markdown | `outputs/reports/*.md` |
| JSON | `outputs/exports/*.json` |

## Error Handling

| Error | Solution |
|-------|----------|
| "Material not found" | Verify ID with `classroom-explorer` |
| "No content to analyze" | Material may be empty |

## Reference

See [reference/output_formats.md] for detailed format specifications.
