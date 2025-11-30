# 🍪 Cookie Setup Guide

This guide explains how to set up cookies to bypass Naukri's bot detection in CI environments.

## Why Use Cookies?

Naukri.com blocks automated login attempts in CI/CD environments (like GitHub Actions) due to:
- Bot detection (headless browsers)
- IP-based blocking
- Rate limiting

Using cookies allows the bot to bypass login entirely, avoiding these issues.

## Step-by-Step Setup

### 1. Generate Cookies Locally

1. **Make sure you're running locally** (not in CI):
   ```bash
   python main.py
   ```

2. **The bot will open a browser window** - DO NOT close it yet

3. **Complete the login process:**
   - Enter your email and password
   - Complete OTP verification if prompted
   - Wait until you see "Login successful!" in the console

4. **Cookies are automatically saved** to `cookies.json`

### 2. Verify Cookies File

Check that `cookies.json` was created:
```bash
ls -la cookies.json
# or on Windows:
dir cookies.json
```

The file should contain JSON data with your session cookies.

### 3. Add Cookies to GitHub

#### Option A: Commit to Repository (Easiest)

```bash
git add cookies.json
git commit -m "Add cookies for automated login"
git push origin master
```

**Note:** This makes your cookies visible in the repository. If you're comfortable with this, it's the simplest approach.

#### Option B: Use GitHub Secrets (More Secure)

1. **Read the cookies file:**
   ```bash
   cat cookies.json
   # or on Windows:
   type cookies.json
   ```

2. **Copy the entire JSON content**

3. **Add to GitHub Secrets:**
   - Go to your repository on GitHub
   - Navigate to **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `NAUKRI_COOKIES`
   - Value: Paste the entire JSON content
   - Click **Add secret**

4. **Update the workflow** to load cookies from secrets (optional - current code uses file)

### 4. Test in GitHub Actions

1. **Trigger the workflow** manually or wait for scheduled run
2. **Check the logs** - you should see:
   ```
   ✅ Logged in using saved cookies!
   ```
   Instead of login attempts

## Troubleshooting

### Cookies Not Working

**Symptoms:**
- Bot still tries to login
- "Cookies expired or invalid" message

**Solutions:**
1. **Regenerate cookies:**
   - Delete `cookies.json`
   - Run locally again
   - Complete login
   - Re-upload cookies

2. **Check cookie format:**
   - Ensure `cookies.json` is valid JSON
   - Should contain an array of cookie objects

3. **Verify cookies are fresh:**
   - Cookies expire after 7-30 days
   - Generate new ones if old

### Access Denied Still Appearing

If you still see "Access Denied" even with cookies:
1. **Cookies might be expired** - regenerate them
2. **IP might be blocked** - try from a different network
3. **Cookies might be invalid** - delete and regenerate

## Security Notes

- **Cookies contain session tokens** - treat them like passwords
- **Don't share cookies** publicly
- **Regenerate cookies** if you suspect they're compromised
- **Use GitHub Secrets** if you want extra security

## Cookie Expiration

Cookies typically expire after:
- **7-30 days** of inactivity
- **When you change your password**
- **When you log out from all devices**

**Solution:** Regenerate cookies periodically or set a reminder to update them monthly.

