# Google Classroom API Reference

Quick reference for classroom-explorer skill.

## Authentication Scopes

Required OAuth2 scopes:

- `classroom.courses.readonly` - List and view courses
- `classroom.coursework.me.readonly` - View coursework
- `classroom.courseworkmaterials.readonly` - View materials
- `classroom.announcements.readonly` - View announcements

## API Endpoints

### Courses

- `GET /v1/courses` - List all courses
- `GET /v1/courses/{id}` - Get specific course

### Coursework

- `GET /v1/courses/{courseId}/courseWork` - List coursework
- `GET /v1/courses/{courseId}/courseWork/{id}` - Get specific

### Materials

- `GET /v1/courses/{courseId}/courseWorkMaterials` - List materials
- `GET /v1/courses/{courseId}/courseWorkMaterials/{id}` - Get specific

### Announcements

- `GET /v1/courses/{courseId}/announcements` - List announcements

## Common Fields

### Course

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier |
| name | string | Course name |
| section | string | Section/period |
| courseState | enum | ACTIVE, ARCHIVED, etc. |
| alternateLink | string | Classroom URL |

### CourseWork

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier |
| title | string | Assignment title |
| workType | enum | ASSIGNMENT, SHORT_ANSWER_QUESTION, etc. |
| maxPoints | number | Maximum points |
| dueDate | object | Due date {year, month, day} |
| materials | array | Attached materials |

### Material Types

| Type | Fields |
|------|--------|
| driveFile | id, title, alternateLink |
| youtubeVideo | id, title |
| link | url, title |
| form | formUrl, title |

## Rate Limits

- Default: 100 requests per 100 seconds per user
- Recommended: Add 60-second retry delay on 429 errors

## Error Codes

| Code | Meaning |
|------|---------|
| 401 | Invalid/expired token |
| 403 | Permission denied |
| 404 | Resource not found |
| 429 | Rate limited |
