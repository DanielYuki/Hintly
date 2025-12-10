---
name: classroom-pdf-analyzer
description: >
  Downloads and analyzes PDF materials from Google Classroom.
  Extracts text and generates AI-powered summaries using OpenAI or Anthropic.
trigger_phrases:
  - "summarize this PDF"
  - "analyze the PDF"
  - "what's in this document"
  - "download and read this PDF"
  - "extract text from PDF"
---

# Classroom PDF Analyzer

Download, extract, and analyze PDF materials from Google Classroom with AI-powered summarization.

## Prerequisites

- ✅ Google OAuth authenticated
- ✅ Google Drive API enabled
- ✅ OpenAI or Anthropic API key (for summarization)

## Features

- 📥 Download PDFs from Google Classroom/Drive
- 📄 Extract text with pdfplumber (primary) or PyPDF2 (fallback)
- 🤖 AI-powered summarization (OpenAI GPT-4o or Anthropic Claude)
- 📊 Automatic chunking for large documents
- 💾 Save summaries as markdown

---

## Commands

### Download PDF

Download a PDF from a Classroom material:

```bash
python {baseDir}/scripts/download_pdf.py \
  --course-id <COURSE_ID> \
  --material-id <MATERIAL_ID> \
  --output <OUTPUT_PATH>  # optional
```

**Output**: PDF downloaded to `outputs/pdfs/`

### Extract Text

Extract text from a downloaded PDF:

```bash
python {baseDir}/scripts/extract_text.py <PDF_PATH> \
  --method pdfplumber \  # or pypdf2
  --output <TEXT_FILE>   # optional
```

**Output**: Extracted text stats and preview

### Summarize PDF

Download, extract, and summarize in one command:

```bash
python {baseDir}/scripts/summarize_pdf.py \
  --course-id <COURSE_ID> \
  --material-id <MATERIAL_ID> \
  --provider openai  # or anthropic (optional)
```

**Flags**:

- `--provider`: Override default LLM provider
- `--no-ai`: Skip AI, just extract text
- `--format`: Output format (markdown or text)

**Output**: Markdown summary saved to `outputs/reports/`

---

## Workflow Example

### Scenario: Summarize Aerodinâmica lecture notes

```bash
# 1. List materials to find PDF
python skills/classroom-explorer/scripts/list_materials.py \
  --course-id 700417862658

# 2. Summarize the PDF (downloads automatically)
python skills/classroom-pdf-analyzer/scripts/summarize_pdf.py \
  --course-id 700417862658 \
  --material-id 700417863604
```

**Output**:

```
✓ Summary complete!

Material: Eq. do potencial completa e linearizada
Course: AED-11 2025/02 - Aerodinâmica Básica
Pages analyzed: 15
Summary saved to: outputs/reports/Eq_do_potencial_completa_e_linearizada_summary.md
```

---

## AI Summarization

### OpenAI (GPT-4o)

- Model: `gpt-4o`
- Best for: General summarization, multilingual content
- Cost: ~$0.005 per page

### Anthropic (Claude 3.5 Sonnet)

- Model: `claude-3-5-sonnet-20241022`
- Best for: Technical content, aerospace engineering
- Cost: ~$0.015 per page

### Configuration

Set in `.env`:

```bash
LLM_PROVIDER=openai  # or anthropic
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Override per-request:

```bash
--provider anthropic
```

---

## Output Format

Summaries include:

- Material title and course info
- Page count and date
- Main topics covered
- Key concepts and equations
- Important points to remember
- Study notes

Example output structure:

````markdown
# [Material Title]

**Course**: [Course Name]
**Date**: 2025-12-10
**Pages**: 15
**Source**: Google Classroom

---

## Main Topics Covered
[AI-generated content]

## Key Concepts
[AI-generated content]

## Study Notes
[AI-generated content]
````

---

## Large Document Handling

For PDFs > 100,000 characters:

1. Automatically chunks into sections
2. Summarizes each chunk
3. Consolidates into final summary

Progress shown:

```
Large PDF: Summarizing in 3 chunks
Summarizing chunk 1/3...
Summarizing chunk 2/3...
Summarizing chunk 3/3...
Generating final summary...
```

---

## Error Handling

### Drive API Not Enabled

```
Error: Google Drive API has not been used in project...
```

**Fix**: Enable at <https://console.developers.google.com/apis/api/drive.googleapis.com>

### No API Key

```
Error: OPENAI_API_KEY not set in .env
```

**Fix**: Add API key to `.env` file

### PDF Extraction Failed

- Retries with PyPDF2 if pdfplumber fails
- May fail on scanned PDFs (no text layer)

---

## Tips

1. **Use `--no-ai` flag** for quick text extraction without API costs
2. **OpenAI GPT-4o-mini** for faster, cheaper summaries (edit llm_client.py)
3. **Check PDF quality** - scanned documents need OCR
4. **Cache downloads** - PDFs saved to `outputs/pdfs/` for reuse

---

## Reference Files

See `reference/` for:

- Supported PDF formats
- Extraction methods comparison
- LLM provider benchmarks
