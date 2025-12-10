---
name: classroom-explorer
description: >
  Navigates and explores Google Classroom data. Lists available courses,
  retrieves coursework and materials, handles authentication. Use when the
  user wants to browse, list, view, or find content in their Google Classroom.
  Triggers: "list my courses", "show assignments", "what's in my class",
  "browse classroom", "get coursework", "show my classes".
---

# Classroom Explorer

Navigate and explore your Google Classroom courses, assignments, and materials.

## Authentication

Before using this skill, ensure (check for) authentication with Google Classroom:

```bash
python {baseDir}/scripts/auth.py --check
```

If not authenticated, start the authentication flow:

```bash
python {baseDir}/scripts/auth.py --setup
```

This opens a browser for Google login. Once complete, credentials are saved automatically.

## Commands

### List All Courses

```bash
python {baseDir}/scripts/list_courses.py
```

Options:

- `--state ACTIVE|ARCHIVED` - Filter by course state
- `--format table|json` - Output format (default: table)

### List Coursework (Assignments)

```bash
python {baseDir}/scripts/list_coursework.py --course-id <COURSE_ID>
```

Options:

- `--format table|json` - Output format

### List Materials

```bash
python {baseDir}/scripts/list_materials.py --course-id <COURSE_ID>
```

Options:

- `--format table|json` - Output format

### Get Specific Item

```bash
python {baseDir}/scripts/get_item.py --course-id <COURSE_ID> --item-id <ITEM_ID> --type coursework|material
```

## Workflow

1. **Check authentication**: `python {baseDir}/scripts/auth.py --check`
2. **If not authenticated**: Run `--setup` and provide login link to user
3. **List courses**: Show available courses, ask user to select
4. **List items**: Based on user's choice, list coursework or materials
5. **Get details**: Fetch specific item details as needed

## Output Examples

### Course List (table format)

```
ID           | Name                  | Section    | State
-------------|----------------------|------------|-------
123456789    | Mathematics 101      | Period 1   | ACTIVE
987654321    | Physics Lab          | Section A  | ACTIVE
```

### Coursework List (table format)

```
ID           | Title                    | Type       | Due Date   | Points
-------------|--------------------------|------------|------------|-------
111222333    | Homework Chapter 5       | ASSIGNMENT | 2024-12-15 | 100
444555666    | Quiz: Derivatives        | QUIZ       | 2024-12-10 | 50
```

## Next Steps

After exploring content, suggest to the user:

- **To summarize or analyze**: Use the **classroom-analyzer** skill
- **To solve an activity**: Use the **classroom-solver** skill

## Error Handling

| Error | Solution |
|-------|----------|
| "Not authenticated" | Run `auth.py --setup` |
| "Course not found" | Verify course ID with `list_courses.py` |
| "Permission denied" | User needs to be enrolled in the course |
| "API rate limit" | Wait 60 seconds and retry |
