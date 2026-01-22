# Quick Deploy Guide for Render

## Step 1: Prepare Environment Variables

Before deploying, have these values ready:

### Required:
- **Pexels API Key**: Get from https://www.pexels.com/api/ (free)
- **n8n Username**: Choose a username (e.g., `admin`)
- **n8n Password**: Choose a strong password

### Auto-configured:
- **Webhook URL**: Will be `https://your-app-name.onrender.com` (replace after knowing your app name)

## Step 2: Deploy on Render

1. Go to https://dashboard.render.com/
2. Click **New +** → **Web Service**
3. Choose **"Build and deploy from a Git repository"**
4. Connect GitHub and select `n8nyoutubeworkflow`

## Step 3: Configure Service

**Service Configuration:**
- **Name**: `n8n-video-maker` (or your choice)
- **Region**: Closest to you
- **Branch**: `main`
- **Runtime**: Docker (auto-detected)
- **Instance Type**: Free

## Step 4: Add Environment Variables

Copy and paste these in Render's Environment section (click "Add Environment Variable"):

| Key | Value | Example |
|-----|-------|---------|
| `N8N_BASIC_AUTH_ACTIVE` | `true` | Required |
| `N8N_BASIC_AUTH_USER` | Your username | `admin` |
| `N8N_BASIC_AUTH_PASSWORD` | Your password | `SecurePass123!` |
| `PEXELS_API_KEY` | Your Pexels key | `abc123xyz...` |
| `WEBHOOK_URL` | Your app URL | `https://n8n-video-maker.onrender.com` |
| `GENERIC_TIMEZONE` | Your timezone | `Asia/Kolkata` |
| `EXECUTIONS_TIMEOUT` | Timeout in seconds | `3600` |

## Step 5: Deploy

1. Click **Create Web Service**
2. Wait 5-10 minutes for first build
3. Access your n8n at: `https://your-app-name.onrender.com`

## Step 6: Keep Service Awake (Free Tier)

The free tier sleeps after 15 minutes. To keep it alive:

1. Go to https://uptimerobot.com (free)
2. Create account
3. Add new monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://your-app-name.onrender.com/healthz`
   - **Interval**: 10 minutes

---

✅ **Done!** Your n8n instance is ready for YouTube Shorts automation.
