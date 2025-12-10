# Google Classroom API Setup Guide

Complete guide to getting Google OAuth2 credentials for Hintly.

## Prerequisites

- Google account (personal or workspace)
- Access to Google Classroom (as teacher or student)

---

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: `Hintly` (or any name)
4. Click **"Create"**
5. Wait for project creation (notification will appear)

---

## Step 2: Enable Google Classroom API

1. In the Cloud Console, select your new project
2. Go to **"APIs & Services"** → **"Library"**
3. Search for **"Google Classroom API"**
4. Click on it and click **"Enable"**
5. Wait for API to be enabled

---

## Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type (unless you have Google Workspace)
3. Click **"Create"**

### Fill in required fields

- **App name**: `Hintly`
- **User support email**: Your email
- **Developer contact**: Your email
- Leave other fields as default

4. Click **"Save and Continue"**

### Add Scopes

5. Click **"Add or Remove Scopes"**
6. Search and select these scopes:
   - `https://www.googleapis.com/auth/classroom.courses.readonly`
   - `https://www.googleapis.com/auth/classroom.coursework.me.readonly`
   - `https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly`
   - `https://www.googleapis.com/auth/classroom.announcements.readonly`

7. Click **"Update"** → **"Save and Continue"**

### Add Test Users

8. Click **"Add Users"**
9. Add your Google email (the one with Classroom access)
10. Click **"Save and Continue"**
11. Review and click **"Back to Dashboard"**

---

## Step 4: Create OAuth2 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Select **"Desktop app"** as application type
4. Name it: `Hintly Desktop Client`
5. Click **"Create"**

### Download Credentials

6. A dialog appears with your Client ID and Client Secret
7. **Option A**: Click **"Download JSON"**
   - Save as `credentials.json` in your `hintly/` directory
   - Update `.env`:

     ```bash
     GOOGLE_CREDENTIALS_PATH=credentials.json
     ```

8. **Option B**: Copy the values manually
   - Copy **Client ID** and **Client Secret**
   - Update `.env`:

     ```bash
     GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
     GOOGLE_CLIENT_SECRET=your_client_secret_here
     ```

---

## Step 5: Configure Your .env File

Create `.env` from `.env.example`:

```bash
cd /Users/dyuki/Desktop/dev/dc/hintly
cp .env.example .env
```

Edit `.env`:

```bash
# Option A: Using credentials.json file
GOOGLE_CREDENTIALS_PATH=credentials.json

# Option B: Using individual values
GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_secret_here

# Optional (leave empty for now)
ANTHROPIC_API_KEY=
```

---

## Step 6: Authenticate

Run the authentication script:

```bash
cd /Users/dyuki/Desktop/dev/dc/hintly
uv run python skills/classroom-explorer/scripts/auth.py --setup
```

This will:

1. Open your browser
2. Ask you to select your Google account
3. Show a warning "Google hasn't verified this app" (this is normal for test apps)
4. Click **"Advanced"** → **"Go to Hintly (unsafe)"**
5. Grant permissions
6. You'll see "The authentication flow has completed"

Your token will be saved to `~/.hintly/token.json`

---

## Step 7: Test It

```bash
# List your courses
uv run python skills/classroom-explorer/scripts/list_courses.py
```

You should see your Google Classroom courses!

---

## Troubleshooting

### "Access blocked: Hintly has not completed the Google verification process"

**Solution**: Make sure you added yourself as a test user in Step 3.8

### "Invalid client" error

**Solution**: Double-check your Client ID and Secret in `.env`

### "Permission denied" error

**Solution**: Verify the scopes in Step 3.6 are correctly added

### "No courses found"

**Solution**: Make sure your Google account has access to Google Classroom courses

---

## About ANTHROPIC_API_KEY

The `ANTHROPIC_API_KEY` is **optional** and not needed for basic functionality:

- **Current use**: None (placeholder for future features)
- **Future use**:
  - AI-generated analysis in `classroom-analyzer`
  - Actual problem solving in `classroom-solver`
  - DSPy integration in Phase 2

**You can leave it empty** for now. The project works without it.

---

## Security Notes

⚠️ **Never commit these files to git**:

- `.env`
- `credentials.json`
- `~/.hintly/token.json`

They're already in `.gitignore` ✓

---

## Next Steps

Once authenticated, try these commands:

```bash
# List courses
uv run python skills/classroom-explorer/scripts/list_courses.py

# List coursework for a course (replace with your course ID)
uv run python skills/classroom-explorer/scripts/list_coursework.py --course-id YOUR_COURSE_ID

# Get course details
uv run python skills/classroom-explorer/scripts/get_item.py --course-id ID --item-id ID --type coursework
```

Or test with Claude in your IDE! 🚀
