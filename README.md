# 🤖 Naukri Automation Bot

Automated job application bot for Naukri.com that searches for DevOps jobs (0-3 years experience) and applies automatically using Selenium WebDriver.

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Step-by-Step Installation](#step-by-step-installation)
- [Configuration](#-configuration)
- [Cookie Setup](#-cookie-setup)
- [Running Locally](#-running-locally)
- [GitHub Actions Setup](#-github-actions-setup)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Disclaimer](#-disclaimer)

## ✨ Features

- **🔐 Cookie-Based Authentication**: Uses saved cookies to bypass login and OTP
- **🔍 Smart Job Search**: Searches for jobs with configurable keywords and experience filter (0-3 years)
- **📝 Auto-Apply**: Automatically applies to jobs when Apply button is available
- **📊 Daily Limit**: Applies to maximum 10 jobs per day (configurable)
- **🔄 Resume Headline Update**: Automatically updates resume headline
- **🛡️ Anti-Detection**: Built-in measures to avoid bot detection
- **📅 Scheduled Runs**: Automated daily runs via GitHub Actions
- **📸 Error Handling**: Comprehensive error handling and logging

## 📦 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **Google Chrome** browser installed
- **Naukri.com account** with valid credentials
- **Git** installed (for version control)
- **GitHub account** (for GitHub Actions)

## 🚀 Step-by-Step Installation

### Step 1: Clone the Repository

Open your terminal/command prompt and run:

```bash
git clone https://github.com/ashishdevops-dev-raj/Naukri-Automation.git
cd Naukri-Automation
```

**What this does:** Downloads the project files to your computer.

---

### Step 2: Install Python Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

**What this installs:**
- `selenium` - Web automation framework
- `webdriver-manager` - Automatic ChromeDriver management
- `python-dotenv` - Environment variable management

**Verify installation:**
```bash
python --version  # Should be 3.8 or higher
pip list  # Verify selenium is installed
```

---

### Step 3: Set Up Environment Variables

Create environment variables for your Naukri credentials and preferences.

#### Option A: Using `.env` file (Recommended for local use)

1. Create a file named `.env` in the project root directory
2. Add the following content:

```env
NAUKRI_EMAIL=your-email@example.com
NAUKRI_PASSWORD=your-password
KEYWORDS=devops engineer
EXPERIENCE_MIN=0
EXPERIENCE_MAX=3
MAX_APPLICATIONS=10
```

#### Option B: Set in Terminal (Temporary)

**Windows (PowerShell):**
```powershell
$env:NAUKRI_EMAIL="your-email@example.com"
$env:NAUKRI_PASSWORD="your-password"
$env:KEYWORDS="devops engineer"
$env:EXPERIENCE_MIN="0"
$env:EXPERIENCE_MAX="3"
$env:MAX_APPLICATIONS="10"
```

**Linux/Mac:**
```bash
export NAUKRI_EMAIL="your-email@example.com"
export NAUKRI_PASSWORD="your-password"
export KEYWORDS="devops engineer"
export EXPERIENCE_MIN="0"
export EXPERIENCE_MAX="3"
export MAX_APPLICATIONS="10"
```

---

### Step 4: Generate Cookies

Cookies are required to bypass login. Follow these steps:

#### Step 4.1: Run Cookie Extraction Script

1. Open `save_cookies.py` in the project
2. Make sure Chrome is installed
3. Run the script:

```bash
python save_cookies.py
```

4. **Manually login** when the browser opens:
   - Enter your email and password
   - Complete OTP verification if prompted
   - Wait until you're logged in

5. The script will generate encoded cookies and save them to `cookies_encoded.txt`

#### Step 4.2: Copy the Encoded Cookies

1. Open `cookies_encoded.txt` file
2. Copy the entire encoded string
3. Save it securely (you'll need it for GitHub Actions)

**Note:** Cookies expire after 7-30 days. You'll need to regenerate them periodically.

---

### Step 5: Test Locally

Before setting up GitHub Actions, test the bot locally:

1. **Set the cookies environment variable:**

**Windows (PowerShell):**
```powershell
$env:NAUKRI_COOKIES_B64="paste-your-encoded-cookies-here"
```

**Linux/Mac:**
```bash
export NAUKRI_COOKIES_B64="paste-your-encoded-cookies-here"
```

2. **Run the bot:**
```bash
python main.py
```

3. **Expected output:**
```
🔐 Logging using encoded cookies....
✅ Cookies decoded as plain JSON
🎯 Cookie login success!
✅ Navigated to homepage
📝 Updating resume headline...
✅ Resume headline updated successfully!
🔎 Searching: https://www.naukri.com/devops-engineer-jobs?experience=0-3
📊 Experience filter: 0-3 years
✅ Found 20 jobs
🔄 Starting to apply to jobs (max 10 per day)...
✅ Applied to job 1 👍
...
🎉 Applied 10 jobs today! (Limit: 10)
```

If it works locally, proceed to GitHub Actions setup.

---

## ⚙️ Configuration

### Environment Variables Explained

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NAUKRI_EMAIL` | Your Naukri email | - | ✅ Yes |
| `NAUKRI_PASSWORD` | Your Naukri password | - | ✅ Yes |
| `NAUKRI_COOKIES_B64` | Base64 encoded cookies | - | ✅ Yes |
| `KEYWORDS` | Job search keywords | "devops engineer" | ❌ No |
| `EXPERIENCE_MIN` | Minimum years of experience | 0 | ❌ No |
| `EXPERIENCE_MAX` | Maximum years of experience | 3 | ❌ No |
| `MAX_APPLICATIONS` | Daily application limit | 10 | ❌ No |

### Customizing Search

**Change keywords:**
```bash
export KEYWORDS="python developer"
```

**Change experience range:**
```bash
export EXPERIENCE_MIN="1"
export EXPERIENCE_MAX="5"
```

**Change daily limit:**
```bash
export MAX_APPLICATIONS="15"
```

---

## 🔄 GitHub Actions Setup

### Step 1: Add GitHub Secrets

1. Go to your GitHub repository: `https://github.com/ashishdevops-dev-raj/Naukri-Automation`
2. Click on **Settings** (top menu)
3. Click on **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret** button
5. Add the following secrets one by one:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `NAUKRI_EMAIL` | your-email@example.com | Your Naukri email |
| `NAUKRI_PASSWORD` | your-password | Your Naukri password |
| `NAUKRI_COOKIES_B64` | paste-encoded-cookies | Cookies from Step 4 |

**How to add each secret:**
- Name: Enter the secret name (e.g., `NAUKRI_EMAIL`)
- Secret: Enter the value (e.g., your email)
- Click **Add secret**
- Repeat for all three secrets

---

### Step 2: Configure Workflow

The workflow file is located at `.github/workflows/daily-run.yml`.

**Current configuration:**
- Runs daily at **9:00 AM IST** (3:30 AM UTC)
- Searches for **"devops engineer"** jobs
- Experience filter: **0-3 years**
- Applies to maximum **10 jobs** per day

**To customize the schedule:**

Edit `.github/workflows/daily-run.yml`:

```yaml
on:
  schedule:
    - cron: "30 3 * * *"   # Change this (UTC time)
```

**Cron format:** `minute hour day month day-of-week`

**Examples:**
- `"0 9 * * *"` - Every day at 9:00 AM UTC
- `"0 */6 * * *"` - Every 6 hours
- `"0 9 * * 1-5"` - Weekdays at 9:00 AM UTC

**To customize search keywords:**

Edit `.github/workflows/daily-run.yml`:

```yaml
env:
  KEYWORDS: "python developer"
  EXPERIENCE_MIN: "0"
  EXPERIENCE_MAX: "3"
```

---

### Step 3: Manual Trigger

You can manually trigger the workflow anytime:

1. Go to **Actions** tab in your repository
2. Select **Auto Apply Naukri Jobs** workflow (left sidebar)
3. Click **Run workflow** button (right side)
4. Click **Run workflow** in the dropdown
5. Wait for the workflow to complete

---

### Step 4: Monitor Workflow Runs

1. Go to **Actions** tab
2. Click on a workflow run to see detailed logs
3. Check for:
   - ✅ Green checkmark = Success
   - ❌ Red X = Failed (check logs for errors)
   - 🟡 Yellow circle = In progress

**Common issues:**
- Missing secrets → Add all required secrets
- Invalid cookies → Regenerate cookies
- Chrome installation failed → Usually auto-fixes on retry

---

## 📁 Project Structure

```
Naukri-Automation/
├── main.py                 # Main entry point - orchestrates the flow
├── login.py                # Cookie-based login and resume headline update
├── search.py               # Job search with experience filter
├── apply.py                # Job application logic
├── config.py               # Configuration settings
├── save_cookies.py          # Script to extract and encode cookies
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── .gitignore              # Git ignore file
└── .github/
    └── workflows/
        └── daily-run.yml   # GitHub Actions workflow
```

### File Descriptions

- **`main.py`**: Main script that runs the entire automation flow
- **`login.py`**: Handles cookie-based authentication and resume headline updates
- **`search.py`**: Searches for jobs with experience filter (0-3 years)
- **`apply.py`**: Applies to jobs with daily limit enforcement
- **`config.py`**: Configuration and environment variable management
- **`save_cookies.py`**: Helper script to extract cookies from browser

---

## 🔧 Troubleshooting

### Issue: "Access Denied" Error

**Symptoms:** Bot shows "Access Denied" message

**Solutions:**
1. **Regenerate cookies** - They may have expired (cookies last 7-30 days)
2. **Check IP blocking** - Try from different network
3. **Verify cookies** - Run locally first to test cookies

**Steps to fix:**
```bash
# 1. Run save_cookies.py again
python save_cookies.py

# 2. Copy new encoded cookies
# 3. Update GitHub secret NAUKRI_COOKIES_B64
```

---

### Issue: "Could not find Apply button"

**Symptoms:** Bot skips jobs with message "Could not find Apply button"

**Possible reasons:**
- Job posting doesn't have an Apply button
- Page structure changed
- Job requires manual application

**Solution:**
- This is normal - bot will skip these jobs and continue
- Check logs to see which jobs were skipped

---

### Issue: Cookies Not Working

**Symptoms:** Login fails even with cookies set

**Solutions:**

1. **Verify cookies format:**
   - Cookies must be base64 encoded
   - Use `save_cookies.py` to generate correctly

2. **Check if cookies expired:**
   - Cookies expire after 7-30 days
   - Regenerate if expired

3. **Verify GitHub secret:**
   - Go to Settings → Secrets
   - Check `NAUKRI_COOKIES_B64` is set correctly
   - No extra spaces or newlines

**Steps to regenerate:**
```bash
python save_cookies.py
# Follow the prompts
# Copy the encoded string
# Update GitHub secret
```

---

### Issue: No Jobs Found

**Symptoms:** Bot finds 0 jobs

**Possible reasons:**
- Search keywords don't match any jobs
- Experience filter too restrictive
- Access Denied on search page

**Solutions:**

1. **Try different keywords:**
   ```bash
   export KEYWORDS="software engineer"
   ```

2. **Adjust experience range:**
   ```bash
   export EXPERIENCE_MIN="0"
   export EXPERIENCE_MAX="5"
   ```

3. **Check manually:**
   - Visit Naukri.com
   - Search with same keywords
   - Verify jobs exist

---

### Issue: GitHub Actions Fails

**Symptoms:** Workflow shows red X (failed)

**Common causes:**

1. **Missing secrets:**
   - Check all 3 secrets are set
   - Verify secret names are exact (case-sensitive)

2. **Invalid cookies:**
   - Regenerate cookies
   - Update `NAUKRI_COOKIES_B64` secret

3. **Chrome installation:**
   - Usually auto-fixes on retry
   - Check workflow logs for specific error

**Steps to debug:**

1. Click on failed workflow run
2. Expand "Run bot" step
3. Check error messages
4. Fix based on error

---

### Issue: Bot Hangs/Stuck

**Symptoms:** Bot runs but doesn't complete

**Solutions:**

1. **Check timeouts:**
   - Bot has 15-second page load timeout
   - Should skip slow-loading pages

2. **Check logs:**
   - Look for last printed message
   - Indicates where it got stuck

3. **Reduce daily limit:**
   ```bash
   export MAX_APPLICATIONS="5"
   ```

---

## 📊 Daily Limits

The bot applies to a maximum of **10 jobs per day** by default.

**To change the limit:**

1. **Via Environment Variable:**
   ```bash
   export MAX_APPLICATIONS=15
   ```

2. **Via GitHub Actions:**
   Edit `.github/workflows/daily-run.yml`:
   ```yaml
   env:
     MAX_APPLICATIONS: "15"
   ```

---

## 🎯 Quick Start Checklist

Follow these steps in order:

- [ ] **Step 1:** Clone the repository
- [ ] **Step 2:** Install dependencies (`pip install -r requirements.txt`)
- [ ] **Step 3:** Set environment variables (email, password, keywords)
- [ ] **Step 4:** Generate cookies using `save_cookies.py`
- [ ] **Step 5:** Test locally (`python main.py`)
- [ ] **Step 6:** Add secrets to GitHub (email, password, cookies)
- [ ] **Step 7:** Push code to GitHub
- [ ] **Step 8:** Verify GitHub Actions workflow runs successfully
- [ ] **Step 9:** Monitor daily runs in Actions tab

---

## ⚠️ Disclaimer

This bot is for **educational and personal use only**. Please:

- ✅ Use responsibly and in accordance with Naukri.com's Terms of Service
- ✅ Respect rate limits and don't abuse the service
- ✅ Review job applications before submitting (when possible)
- ⚠️ Be aware that automated applications may violate some job posting terms
- ⚠️ The authors are not responsible for any misuse of this tool

**Use at your own risk.**

---

## 📝 License

This project is open source and available for personal use.

---


**Happy Job Hunting! 🚀**
