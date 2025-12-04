# 🤖 Naukri Automation Bot

Automated job application bot for Naukri.com that searches for DevOps jobs and applies automatically using Selenium WebDriver.

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Cookie Setup](#-cookie-setup)
- [Running Locally](#-running-locally)
- [GitHub Actions Setup](#-github-actions-setup)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Disclaimer](#-disclaimer)

## ✨ Features

- **🔐 Cookie-Based Authentication**: Uses saved cookies to bypass login and OTP
- **🔍 Smart Job Search**: Searches for jobs with configurable keywords and location
- **📝 Auto-Apply**: Automatically applies to jobs when Apply button is available
- **📊 Daily Limit**: Applies to maximum 7 jobs per day (configurable)
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

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/ashishdevops-dev-raj/Naukri-Automation.git
cd Naukri-Automation
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `selenium` - Web automation framework
- `webdriver-manager` - Automatic ChromeDriver management
- `python-dotenv` - Environment variable management

### Step 3: Verify Installation

```bash
python --version  # Should be 3.8 or higher
pip list  # Verify selenium is installed
```

## ⚙️ Configuration

### Environment Variables

The bot uses environment variables for configuration. Create a `.env` file in the project root:

```bash
# Required
NAUKRI_EMAIL=your-email@example.com
NAUKRI_PASSWORD=your-password

# Optional
KEYWORDS=devops engineer
LOCATION=bangalore
MAX_APPLICATIONS=7
```

**Or set them in your terminal:**

**Windows (PowerShell):**
```powershell
$env:NAUKRI_EMAIL="your-email@example.com"
$env:NAUKRI_PASSWORD="your-password"
$env:KEYWORDS="devops engineer"
$env:LOCATION="bangalore"
$env:MAX_APPLICATIONS="7"
```

**Linux/Mac:**
```bash
export NAUKRI_EMAIL="your-email@example.com"
export NAUKRI_PASSWORD="your-password"
export KEYWORDS="devops engineer"
export LOCATION="bangalore"
export MAX_APPLICATIONS="7"
```

## 🍪 Cookie Setup

### Why Cookies?

Naukri.com blocks automated login in CI/CD environments. Using cookies allows the bot to bypass login entirely.

### Step-by-Step Cookie Generation

#### Step 1: Run Bot Locally (Non-Headless)

1. **Temporarily modify `main.py`** to run in non-headless mode:

```python
# Comment out or remove this line:
# chrome_options.add_argument("--headless=new")
```

2. **Run the bot locally:**
```bash
python main.py
```

3. **Complete login manually:**
   - The bot will open a browser window
   - Enter your email and password
   - Complete OTP verification if prompted
   - Wait for successful login

#### Step 2: Extract Cookies

You need to extract cookies from your browser session. Here's a Python script to help:

```python
# save_cookies.py
import json
import gzip
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Setup driver (non-headless)
options = Options()
driver = webdriver.Chrome(options=options)

# Login manually, then run:
driver.get("https://www.naukri.com/mnjuser/homepage")
cookies = driver.get_cookies()

# Compress and encode
cookies_json = json.dumps(cookies)
compressed = gzip.compress(cookies_json.encode('utf-8'))
encoded = base64.b64encode(compressed).decode('utf-8')

print("Your encoded cookies:")
print(encoded)

# Save to file
with open('cookies_encoded.txt', 'w') as f:
    f.write(encoded)

driver.quit()
```

#### Step 3: Add Cookies to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `NAUKRI_COOKIES_B64`
5. Value: Paste the encoded cookie string
6. Click **Add secret**

**Note:** Cookies expire after 7-30 days. You'll need to regenerate them periodically.

## 🏃 Running Locally

### Step 1: Set Environment Variables

```bash
# Windows PowerShell
$env:NAUKRI_COOKIES_B64="your-encoded-cookies-here"
$env:KEYWORDS="devops engineer"
$env:LOCATION="bangalore"
$env:MAX_APPLICATIONS="7"

# Linux/Mac
export NAUKRI_COOKIES_B64="your-encoded-cookies-here"
export KEYWORDS="devops engineer"
export LOCATION="bangalore"
export MAX_APPLICATIONS="7"
```

### Step 2: Run the Bot

```bash
python main.py
```

### Step 3: Monitor Output

The bot will:
1. ✅ Login using cookies
2. 📝 Update resume headline (optional)
3. 🔍 Search for jobs
4. 📤 Apply to jobs (up to daily limit)
5. 📊 Show summary

**Example Output:**
```
🔐 Logging using encoded cookies....
✅ Cookies decoded as plain JSON
🎯 Cookie login success!
✅ Navigated to homepage
📝 Updating resume headline (optional step)...
🔎 Searching: https://www.naukri.com/devops-engineer-jobs-in-bangalore
✅ Found 21 jobs
🔄 Starting to apply to jobs (max 7 per day)...
✅ Applied to job 1 👍
✅ Applied to job 2 👍
...
🎉 Applied 7 jobs today! (Limit: 7)
```

## 🔄 GitHub Actions Setup

### Step 1: Add GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:

| Secret Name | Description | Required |
|------------|-------------|----------|
| `NAUKRI_EMAIL` | Your Naukri email | ✅ Yes |
| `NAUKRI_PASSWORD` | Your Naukri password | ✅ Yes |
| `NAUKRI_COOKIES_B64` | Base64 encoded cookies | ✅ Yes |

### Step 2: Configure Workflow

The workflow file is located at `.github/workflows/daily-run.yml`. It's already configured to:

- Run daily at **9:00 AM IST** (3:30 AM UTC)
- Search for **"devops engineer"** jobs in **"bangalore"**
- Apply to maximum **7 jobs** per day

**To customize the schedule:**

Edit `.github/workflows/daily-run.yml`:

```yaml
on:
  schedule:
    - cron: "30 3 * * *"   # Change this (UTC time)
```

**Cron format:** `minute hour day month day-of-week`

**To customize search:**

Edit the environment variables in the workflow:

```yaml
env:
  KEYWORDS: "your-keyword"
  LOCATION: "your-location"
```

### Step 3: Manual Trigger

You can manually trigger the workflow:

1. Go to **Actions** tab in your repository
2. Select **Auto Apply Naukri Jobs** workflow
3. Click **Run workflow**
4. Click **Run workflow** button

### Step 4: Monitor Workflow Runs

1. Go to **Actions** tab
2. Click on a workflow run to see logs
3. Check for any errors or issues

## 📁 Project Structure

```
Naukri-Automation/
├── main.py                 # Main entry point
├── login.py                # Cookie-based login and resume headline update
├── search.py               # Job search functionality
├── apply.py                # Job application logic
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── .github/
    └── workflows/
        └── daily-run.yml   # GitHub Actions workflow
```

### File Descriptions

- **`main.py`**: Orchestrates the entire automation flow
- **`login.py`**: Handles cookie-based authentication and resume updates
- **`search.py`**: Searches for jobs and extracts job links
- **`apply.py`**: Applies to jobs with daily limit enforcement
- **`config.py`**: Configuration and environment variable management

## 🔧 Troubleshooting

### Issue: "Access Denied" Error

**Solution:**
- Regenerate cookies (they may have expired)
- Check if your IP is blocked
- Try running locally first to verify cookies work

### Issue: "Stale Element Reference" Error

**Solution:**
- This is fixed in the latest version
- The bot now extracts job links as strings instead of element references
- Update to the latest code

### Issue: "Could not find Apply button"

**Possible reasons:**
- Job posting doesn't have an Apply button
- Page structure changed
- Job requires manual application

**Solution:**
- The bot will skip these jobs and continue
- Check logs for details

### Issue: Cookies Not Working

**Solution:**
1. Verify cookies are correctly encoded
2. Check if cookies have expired (regenerate if needed)
3. Ensure `NAUKRI_COOKIES_B64` secret is set correctly in GitHub

### Issue: No Jobs Found

**Possible reasons:**
- Search keywords don't match any jobs
- Location filter too restrictive
- Access Denied on search page

**Solution:**
- Try different keywords or location
- Check if you can access the search page manually
- Verify cookies are valid

### Issue: GitHub Actions Fails

**Common causes:**
1. Missing secrets
2. Invalid cookies
3. Chrome/ChromeDriver issues

**Solution:**
1. Verify all required secrets are set
2. Regenerate cookies
3. Check workflow logs for specific errors

## 📊 Daily Limits

The bot applies to a maximum of **7 jobs per day** by default. This can be changed:

1. **Via Environment Variable:**
   ```bash
   export MAX_APPLICATIONS=10
   ```

2. **Via GitHub Actions:**
   Edit `.github/workflows/daily-run.yml`:
   ```yaml
   env:
     MAX_APPLICATIONS: "10"
   ```

## ⚠️ Disclaimer

This bot is for **educational and personal use only**. Please:

- ✅ Use responsibly and in accordance with Naukri.com's Terms of Service
- ✅ Respect rate limits and don't abuse the service
- ✅ Review job applications before submitting (when possible)
- ⚠️ Be aware that automated applications may violate some job posting terms
- ⚠️ The authors are not responsible for any misuse of this tool

**Use at your own risk.**

## 📝 License

This project is open source and available for personal use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review GitHub Issues
3. Create a new issue with detailed error logs

## 🎯 Quick Start Checklist

- [ ] Clone the repository
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Generate cookies locally
- [ ] Add cookies to GitHub Secrets
- [ ] Configure environment variables
- [ ] Test locally (`python main.py`)
- [ ] Push to GitHub
- [ ] Verify GitHub Actions workflow runs successfully

---

**Happy Job Hunting! 🚀**
