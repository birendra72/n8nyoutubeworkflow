# n8n YouTube Shorts Automation 🎥

Automate YouTube Shorts creation with AI voice narration and background videos using n8n workflows on Render's free tier with persistent PostgreSQL storage.

## 🌟 Features

- **Custom n8n Docker Image** with Python and FFmpeg pre-installed
- **AI Voice Generation** using Microsoft Edge TTS
- **Automated Video Creation** with background footage
- **Free Deployment** on Render
- **Persistent Storage** via Neon.tech PostgreSQL (Free)
- **Scheduled Automation** via n8n workflows

## 📋 Prerequisites

- GitHub account (to host this repository)
- [Render](https://render.com) account (free tier)
- [Neon.tech](https://neon.tech) account (free PostgreSQL database)
- [Pexels API Key](https://www.pexels.com/api/) (free, for stock videos)

---

## 🚀 Quick Start Guide

### Phase 1: Set Up Free PostgreSQL Database (Neon.tech)

> **Why Do We Use Neon.tech PostgreSQL?**  
> Render's free tier **goes to sleep after 15 minutes of inactivity**. When it wakes up or restarts, it uses "Ephemeral Storage" - meaning all data stored locally (workflows, credentials, settings) gets wiped clean, like a hotel room reset after checkout.  
>   
> By using **Neon.tech's free PostgreSQL database**, we store all n8n data externally. So even when Render sleeps and wakes up, your workflows and API credentials remain intact because they're safely stored in the cloud database, not on Render's temporary storage.

1. Go to **[Neon.tech](https://neon.tech)** and click **Sign Up**
   - You can use your GitHub or Google account

2. Create a **New Project**:
   - **Name:** `n8n-memory` (or any name you prefer)
   - **Region:** Choose the one closest to you (e.g., US East, Europe)
   - **Version:** Default (Postgres 15 or 16)

3. **Copy the Connection Details**:
   - Neon will show you a "Connection String" that looks like this:
     ```
     postgres://alex:AbCd123@ep-shiny-rain-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
     ```
   - **Do NOT close this tab yet** - you'll need to extract values from this string

4. **Extract Database Credentials** from the connection string:
   - **Host:** The part after `@` and before `/`
     - Example: `ep-shiny-rain-123456.us-east-2.aws.neon.tech`
   - **User:** The part after `//` and before `:`
     - Example: `alex`
   - **Password:** The part after `:` and before `@`
     - Example: `AbCd123`
   - **Database:** The part after `/` and before `?`
     - Example: `neondb`

---

### Phase 2: Deploy to Render

1. **Fork or Clone this Repository** to your GitHub account

2. Go to [Render Dashboard](https://dashboard.render.com/)

3. Click **New +** → **Web Service**

4. Choose **"Build and deploy from a Git repository"**

5. Connect your GitHub account and select this repository (`n8nyoutubeworkflow`)

6. **Configure the Service:**
   - **Name:** `n8n-video-maker` (or any name you prefer)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Runtime:** Docker (auto-detected from Dockerfile)
   - **Instance Type:** Free

7. **Environment Variables** - Add ALL of these in Render's Environment tab:

   #### **Basic n8n Configuration:**
   ```
   N8N_BASIC_AUTH_ACTIVE=true
   N8N_BASIC_AUTH_USER=admin
   N8N_BASIC_AUTH_PASSWORD=YourSecurePassword123!
   N8N_RUNNERS_DISABLED=true
   ```

   #### **PostgreSQL Database Configuration:**
   > Use the values extracted from your Neon connection string
   
   | Variable Name | Value | Example |
   |---------------|-------|---------|
   | `DB_TYPE` | `postgresdb` | Required |
   | `DB_POSTGRESDB_HOST` | Your Neon host | `ep-shiny-rain-123456.us-east-2.aws.neon.tech` |
   | `DB_POSTGRESDB_PORT` | `5432` | Default PostgreSQL port |
   | `DB_POSTGRESDB_DATABASE` | Your database name | `neondb` |
   | `DB_POSTGRESDB_USER` | Your database user | `alex` |
   | `DB_POSTGRESDB_PASSWORD` | Your database password | `AbCd123` |
   | `DB_POSTGRESDB_SSL_ALLOW_SELF_SIGNED` | `true` | Required for Neon SSL |

   #### **Encryption Key (CRITICAL):**
   > ⚠️ **IMPORTANT:** This key encrypts your API credentials. Write it down and keep it safe!
   
   ```
   N8N_ENCRYPTION_KEY=s0m3_v3ry_l0ng_r4nd0m_p4ssw0rd_h3r3
   ```
   - Make up a long random string (at least 24 characters)
   - **Write this down** - if you move n8n to a new server, you'll need this exact key

   #### **API Keys & Configuration:**
   ```
   PEXELS_API_KEY=your_pexels_api_key_here
   WEBHOOK_URL=https://your-app-name.onrender.com
   GENERIC_TIMEZONE=Asia/Kolkata
   EXECUTIONS_TIMEOUT=3600
   N8N_CONCURRENCY_PRODUCTION_LIMIT=1
   ```

   > **Get Your Pexels API Key:**
   > 1. Go to https://www.pexels.com/api/
   > 2. Sign up for free
   > 3. Copy your API key

8. Click **"Save Changes"** in the Environment tab

9. Click **"Create Web Service"** (or "Manual Deploy" if already created)

10. Wait for deployment (first build takes 5-10 minutes)

---

### Phase 3: First-Time Setup & Verification

1. Once deployment is complete, open your n8n URL:
   ```
   https://your-app-name.onrender.com
   ```

2. **Create Owner Account** (First Time Only):
   - You'll be asked to create an account
   - This is normal when switching from SQLite to PostgreSQL
   - Create your account credentials

3. **Test Persistence**:
   - Create a simple workflow
   - Go to Render → Click **"Restart Service"**
   - Wait for restart (2-3 minutes)
   - Open your n8n URL again
   - **Your workflow should still be there!** 🎉

---

## 🎬 Creating Your First Workflow

### Option 1: Import Pre-Built Workflow (Recommended)

1. Download one of the workflow JSON files from this repository:
   - `workflow-simple-test.json` - Basic test workflow
   - `workflow-automated-trends.json` - Advanced daily automation

2. In n8n, click **"+"** → **"Import from File"**

3. Select the downloaded JSON file

4. Configure any API credentials if needed

5. Activate the workflow

### Option 2: Build From Scratch

#### **Node 1: Schedule Trigger**
- **Trigger:** Cron
- **Mode:** Every Day
- **Hour:** 8
- **Minute:** 0

#### **Node 2: Set Script Data**
- **Node Type:** Set
- **Values:**
  ```json
  {
    "script": "Welcome to today's motivational tip. Success is not final, failure is not fatal. It is the courage to continue that counts.",
    "search_term": "nature landscape"
  }
  ```

#### **Node 3: Execute Command**
- **Node Type:** Execute Command
- **Command:** `python3`
- **Arguments:**
  ```
  /home/node/shorts_maker.py
  {{ $json.script }}
  {{ $json.search_term }}
  ```

#### **Node 4: Read Video File**
- **Node Type:** Read Binary File
- **File Path:** `/tmp/final_short.mp4`
- **Property Name:** `video`

#### **Node 5: Upload to YouTube** (Optional)
- Use the HTTP Request node or YouTube API node
- Configure with your YouTube API credentials

---

## 🛠️ How It Works

1. **Scheduled Trigger** fires at your specified time
2. **Script Data** defines the narration text and video search term
3. **Execute Command** runs the Python script that:
   - Generates AI voice using Edge-TTS
   - Downloads background video from Pexels
   - Combines audio + video with FFmpeg
   - Outputs final video to `/tmp/final_short.mp4`
4. **Read Binary File** loads the generated video
5. **Upload** (optional) to YouTube or other platforms
6. **PostgreSQL** saves your workflow configuration permanently

---

## 🎨 Customization

### Change AI Voice

Edit `shorts_maker.py` line 17:
```python
voice = "en-US-AriaNeural"  # Try: en-GB-SoniaNeural, en-AU-NatashaNeural, etc.
```

[Full list of voices](https://speech.microsoft.com/portal/voicegallery)

### Video Duration

Edit `shorts_maker.py` line 99:
```python
'-t', '60',  # Change to desired duration (max 60 for Shorts)
```

### Video Quality

Edit FFmpeg parameters in `shorts_maker.py` for resolution/bitrate adjustments

### Schedule Times

Edit the Cron expression in the Schedule Trigger node:
- Daily at 8 AM: `0 8 * * *`
- Every 2 hours: `0 */2 * * *`
- Twice daily (8 AM & 8 PM): `0 8,20 * * *`

---

## ⚠️ Important Notes

### Render Free Tier Limitations

- **Sleep After 15 Minutes:** Your n8n instance will sleep if inactive
- **Solution:** Use [UptimeRobot](https://uptimerobot.com) (free) to ping your instance every 10 minutes:
  ```
  https://your-app-name.onrender.com/healthz
  ```

### Storage Behavior

- **Workflows, Credentials, Settings:** Stored permanently in Neon PostgreSQL ✅
- **Generated Videos:** Stored in `/tmp` (ephemeral) - Will be deleted on restart ⚠️
- **Solution:** Always upload/download videos within the same workflow execution

### Encryption Key Security

- **Never lose your `N8N_ENCRYPTION_KEY`** - Without it, you cannot decrypt saved credentials
- Store it securely (password manager, secure notes, etc.)
- If you migrate to a new server, you need this exact key

---

## 🐛 Troubleshooting

### "Database connection failed"

❌ **Problem:** Incorrect PostgreSQL credentials

✅ **Solution:**
- Double-check all `DB_POSTGRESDB_*` values match your Neon connection string
- Ensure `DB_POSTGRESDB_SSL_ALLOW_SELF_SIGNED=true` is set
- Check Neon project is active and not paused

### "Workflows disappear after restart"

❌ **Problem:** Not using PostgreSQL (still using SQLite)

✅ **Solution:**
- Verify `DB_TYPE=postgresdb` is set in Render environment
- Redeploy the service after adding DB variables

### "python3: command not found"

❌ **Problem:** Using standard n8n image instead of custom one

✅ **Solution:** Make sure you deployed from **this GitHub repository**, not from Docker Hub

### FFmpeg Errors

❌ **Problem:** Video dimensions or codec issues

✅ **Solution:** Check the background video format. The script expects MP4. Modify FFmpeg parameters if needed.

### No Videos Found

❌ **Problem:** Pexels API key not set or invalid search term

✅ **Solution:** 
- Verify `PEXELS_API_KEY` is set in Render environment variables
- Try different search terms (e.g., "ocean", "city", "mountains")

### Workflow Not Triggering

❌ **Problem:** Instance is asleep

✅ **Solution:** Set up UptimeRobot to keep your instance awake

### "Virtual environment is missing"

❌ **Problem:** `N8N_RUNNERS_DISABLED` not set

✅ **Solution:**
- Add `N8N_RUNNERS_DISABLED=true` to Render environment
- Redeploy the service

---

## 📚 Resources

- [n8n Documentation](https://docs.n8n.io/)
- [Render Documentation](https://render.com/docs)
- [Neon.tech Documentation](https://neon.tech/docs)
- [Pexels API Docs](https://www.pexels.com/api/documentation/)
- [Edge-TTS Voices](https://github.com/rany2/edge-tts)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

---

## 🎓 YouTube API Setup (For Automated Uploads)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Create **OAuth 2.0 credentials**
5. Add authorized redirect URI: `https://your-app.onrender.com/rest/oauth2-credential/callback`
6. In n8n:
   - Settings → Credentials → Add Credential
   - Select "YouTube OAuth2 API"
   - Enter Client ID and Client Secret
   - Click "Connect my account"
   - Authorize access

---

## 📝 License

MIT License - Feel free to modify and use for your projects!

## 🤝 Contributing

Issues and pull requests are welcome! Feel free to improve the script or documentation.

---

**Made with ❤️ for automated content creation**
