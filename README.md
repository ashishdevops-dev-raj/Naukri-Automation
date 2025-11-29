# Naukri Automation Bot 🤖

Automated job application bot for Naukri.com that searches for jobs and applies automatically using Selenium.

## 📋 Project Summary

This bot automates the job application process on Naukri.com by:
- Logging in securely using environment variables
- Searching for jobs based on configured criteria
- Automatically applying to jobs when apply buttons are available
- Respecting daily application limits
- Logging all activities and capturing screenshots on errors

## ✨ Features

- **Secure Login**: Uses environment variables for credentials (no hardcoded secrets)
- **Popup Handling**: Automatically handles various popups that appear after login
- **Job Search**: Configurable search with keyword and location filters
- **Auto-Apply**: Automatically applies to jobs if apply button exists
- **Apply Limit**: Configurable limit per run to prevent over-application
- **Error Handling**: Saves screenshots on errors for debugging
- **Detailed Logging**: Comprehensive logs with timestamps
- **GitHub Actions**: Automated daily runs at 9 AM IST

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- Naukri.com account

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd naukri-automation-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:

**Windows (PowerShell)**
```powershell
$env:NAUKRI_EMAIL="your-email@example.com"
$env:NAUKRI_PASSWORD="your-password"
```

**Linux/Mac**
```bash
export NAUKRI_EMAIL="your-email@example.com"
export NAUKRI_PASSWORD="your-password"
```

## 🏃 How to Run Locally

1. Set environment variables (see above)

2. Run the bot:
```bash
python main.py
```

3. Monitor logs:
   - Console output for real-time updates
   - `logs/naukri_bot_YYYYMMDD.log` for detailed logs
   - `screenshots/` folder for error screenshots

## 🔄 How to Run in GitHub Actions

### Setup Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:
   - `NAUKRI_EMAIL`: Your Naukri email
   - `NAUKRI_PASSWORD`: Your Naukri password

### Workflow Configuration

The workflow is configured in `.github/workflows/naukri.yml` and will:
- Run automatically every day at 9 AM IST (3:30 AM UTC)
- Can be manually triggered via `workflow_dispatch`
- Install dependencies
- Run the bot
- Upload screenshots as artifacts on failure

### Manual Trigger

1. Go to **Actions** tab in your repository
2. Select **Naukri Automation** workflow
3. Click **Run workflow**

## 📝 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NAUKRI_EMAIL` | Your Naukri.com email | ✅ Yes | - |
| `NAUKRI_PASSWORD` | Your Naukri.com password | ✅ Yes | - |
| `SEARCH_KEYWORD` | Job search keyword | No | "Python Developer" |
| `SEARCH_LOCATION` | Job location | No | "Bangalore" |
| `MAX_SEARCH_PAGES` | Maximum pages to search | No | 3 |
| `MAX_JOBS_TO_APPLY` | Maximum jobs to process | No | 10 |
| `APPLY_LIMIT` | Maximum applications per run | No | 5 |
| `DELAY_BETWEEN_APPLICATIONS` | Delay in seconds | No | 3 |
| `SCREENSHOT_DIR` | Screenshot directory | No | "screenshots" |

## 📁 Folder Structure

```
naukri-automation-bot/
├── main.py              # Main entry point
├── login.py             # Login module
├── search.py            # Job search module
├── apply.py             # Auto-apply module
├── config.py            # Configuration module
├── requirements.txt     # Python dependencies
├── utils/
│   ├── logger.py       # Logging utilities
│   └── helpers.py      # Helper functions
├── logs/                # Log files (auto-created)
├── screenshots/         # Error screenshots (auto-created)
└── .github/
    └── workflows/
        └── naukri.yml   # GitHub Actions workflow
```

## 📸 Screenshots

When errors occur, screenshots are automatically saved to the `screenshots/` directory with timestamps:
- `login_failed_YYYYMMDD_HHMMSS.png`
- `timeout_error_YYYYMMDD_HHMMSS.png`
- `apply_error_job_X_YYYYMMDD_HHMMSS.png`

These screenshots help diagnose issues with:
- Login failures
- Page load timeouts
- Application errors
- Unexpected page structures

## ⚠️ Disclaimer

This bot is for educational and personal use only. Please:
- Use responsibly and in accordance with Naukri.com's Terms of Service
- Respect rate limits and don't abuse the service
- Review job applications before submitting (when possible)
- Be aware that automated applications may violate some job posting terms
- The authors are not responsible for any misuse of this tool

**Use at your own risk.**
