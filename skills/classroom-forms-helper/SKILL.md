---
name: classroom-forms-helper
description: >
  Reads Google Forms structure from Classroom activities.
  Analyzes questions and generates answer templates.
trigger_phrases:
  - "analyze this form"
  - "what questions are in this quiz"
  - "help me with this form"
  - "prepare for this quiz"
---

# Classroom Forms Helper

Read, analyze, and prepare for Google Forms linked from Classroom activities.

## Prerequisites

- ✅ Google OAuth authenticated
- ✅ Google Forms API enabled (will prompt if not)
- ✅ OpenAI or Anthropic API key (for analysis)

## Features

- 📋 Read form structure and questions
- 🤖 AI-powered question analysis
- 📝 Generate answer templates
- 📊 Categorize question types

---

## Commands

### Get Form Structure

Read form questions:

```bash
python {baseDir}/scripts/get_form.py <FORM_URL> \
  --format table  # or json
```

### Analyze Questions

AI analysis of form content:

```bash
python {baseDir}/scripts/analyze_form.py <FORM_URL> \
  --provider openai  # optional
```

### Generate Template

Create answer template:

```bash
python {baseDir}/scripts/generate_template.py <FORM_URL> \
  --output <PATH>  # optional
```

---

## Workflow Example

```bash
# 1. Get form structure
PYTHONPATH=. uv run python skills/classroom-forms-helper/scripts/get_form.py \
  "https://docs.google.com/forms/d/1ABC123/viewform"

# 2. Analyze with AI
PYTHONPATH=. uv run python skills/classroom-forms-helper/scripts/analyze_form.py \
  "https://docs.google.com/forms/d/1ABC123/viewform"

# 3. Generate study template
PYTHONPATH=. uv run python skills/classroom-forms-helper/scripts/generate_template.py \
  "https://docs.google.com/forms/d/1ABC123/viewform"
```

---

## ⚠️ Important Limitations

### Google Forms API Restrictions

The Google Forms API has **significant limitations** that affect this skill:

**What Works** ✅:

- Forms you personally created
- Forms you own in your Google account

**What Doesn't Work** ❌:

- Forms assigned by teachers in Classroom
- Forms shared with you (even if you can view them)
- Public forms (even if accessible via browser)
- Submitting responses (API restriction)

### Why This Happens

Google Forms API only allows access to forms where you are the **owner**. This is a Google API design decision, not a limitation of this implementation.

**Impact**: This skill has limited use for student workflows since most Classroom forms are created by teachers.

---

## 🔄 Alternative: Browser Automation (Future)

To work around API limitations, browser automation could be used:

### Option 1: Playwright (Recommended)

```python
# Future implementation concept
from playwright.sync_api import sync_playwright

def scrape_form_questions(form_url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(form_url)
        
        # Extract questions from DOM
        questions = page.query_selector_all('.freebirdFormviewerComponentsQuestionBaseTitle')
        # ... extract and parse
```

**Pros**:

- Works with ANY form (public, shared, assigned)
- Can screenshot questions
- Can interact with form elements

**Cons**:

- Slower than API
- Requires browser installation
- More fragile (breaks if Google changes HTML)

### Option 2: Selenium

Similar to Playwright but older technology.

### Option 3: Browser Subagent

Use the existing `browser_subagent` tool to navigate and extract form content.

---

## Current Recommendation

**For now**: Use the PDF Analyzer skill for course materials. It works excellently and provides real value.

**For forms**:

1. If you create study forms yourself, this skill works
2. For teacher-assigned forms, browser automation would be needed (Phase 3)

---

## Supported Question Types

- ✅ Multiple Choice
- ✅ Short Answer
- ✅ Paragraph
- ✅ Scale (1-5, etc.)
- ✅ Date
- ✅ Time
- ✅ Checkboxes

---

## AI Analysis Features

- Topic identification
- Difficulty estimation
- Study recommendations
- Key concepts to review

---

## Limitations

- **Read-only**: Cannot submit form responses (Google API restriction)
- **Public forms**: Works best with forms accessible via link
- **No responses**: Cannot read other students' answers

---

## Tips

1. Use analyze_form for study prep
2. Generate template before quiz to organize answers
3. Compare form structure across different quizzes
