# n8n YouTube Shorts Automation 🎥

Automate YouTube Shorts creation with AI voice narration and background videos using n8n workflows on Render's free tier with persistent PostgreSQL storage and Hugging Face Spaces for video processing.

## 🌟 Features

- **Custom n8n Docker Image** with Python and FFmpeg pre-installed
- **AI Voice Generation** using Microsoft Edge TTS
- **Automated Video Creation** with background footage
- **Free Deployment** with Render (n8n) + Hugging Face Spaces (video engine)
- **Persistent Storage** via Neon.tech PostgreSQL (Free)
- **Scheduled Automation** via n8n workflows
- **16GB RAM Video Processing** on Hugging Face Spaces (vs 512MB on Render)

## 🏗️ Architecture

This project uses a **split architecture** to overcome Render's RAM limitations:

- **Render (n8n)**: Workflow orchestration, RSS parsing, AI script generation, scheduling
- **Hugging Face Space**: Video generation (FFmpeg processing with 16GB RAM)
- **Neon.tech**: Persistent PostgreSQL database for workflows and credentials

## 📋 Prerequisites

- GitHub account (to host this repository)
- [Render](https://render.com) account (free tier)
- [Hugging Face](https://huggingface.co) account (free tier)
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

### Phase 2: Set Up Hugging Face Space (Video Engine)

> **Why Use Hugging Face Spaces?**  
> Render's free tier has only **512MB of RAM**, which is insufficient for FFmpeg video processing (requires 2GB+ RAM). The process gets killed (Error 137) when memory exceeds the limit.  
>   
> **Hugging Face Spaces** offers **16GB of RAM** on the free tier, perfect for video generation. We'll create a simple API endpoint that n8n can call to generate videos.

1. **Create a New Space:**
   - Go to [Hugging Face Spaces](https://huggingface.co/new-space)
   - Click **"Create new Space"**
   - **Name:** `n8n-video-engine` (or any name)
   - **SDK:** Docker
   - **Hardware:** CPU basic (free)
   - **Visibility:** Public or Private (your choice)
   - Click **"Create Space"**

2. **Clone Your Space Repository:**
   
   ```powershell
   # Clone the Space (use your Hugging Face username)
   git clone https://huggingface.co/spaces/YOUR-USERNAME/n8n-video-engine
   cd n8n-video-engine
   ```

3. **Copy Hugging Face Files:**
   
   From this repository's `huggingface/` folder, copy these files to your Space:
   - `Dockerfile`
   - `requirements.txt`
   - `app.py`
   - `README.md`

   ```powershell
   # Example (adjust paths as needed)
   cp ../n8nyoutubeworkflow/huggingface/* .
   ```

4. **Push to Hugging Face:**
   
   ```powershell
   git add .
   git commit -m "Initial video generation service"
   git push
   ```
   
   > When prompted for credentials:
   > - **Username:** Your Hugging Face username
   > - **Password:** Use an [Access Token](https://huggingface.co/settings/tokens) with **WRITE** permissions

5. **Configure the Pexels API Key:**
   - Go to your Space page on Hugging Face
   - Click **Settings** → **Variables and secrets**
   - Click **"New secret"**
   - **Name:** `PEXELS_API_KEY`
   - **Value:** Your Pexels API key (from [pexels.com/api](https://www.pexels.com/api/))
   - Click **"Save"**

6. **Wait for Build:**
   - The Space will build automatically (takes 2-3 minutes)
   - Watch the build logs in the **"Logs"** tab
   - Wait until status shows **"Running"** (green checkmark)

7. **Get Your Space URL:**
   - Once running, click the **three dots (⋯)** in the top right
   - Select **"Embed this space"** → **"Direct URL"**
   - Copy the URL (e.g., `https://yourname-n8n-video-engine.hf.space`)
   - **Save this URL** - you'll need it for n8n configuration

---

### Phase 3: Deploy n8n to Render

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

## 🎬 Setting Up Your Workflow

### Import the Updated Workflow

1. **Update the Workflow JSON:**
   - Open `Trend to Script (A4F Integrated - Full Pipeline).json` in a text editor
   - Find the line with `"url": "https://YOUR-SPACE-NAME.hf.space/generate"`
   - Replace `YOUR-SPACE-NAME` with your actual Hugging Face Space URL
   - Save the file

2. **Import to n8n:**
   - In n8n, click **"+"** → **"Import from File"**
   - Select the updated `Trend to Script (A4F Integrated - Full Pipeline).json`
   - Click **"Import"**

3. **Verify the Workflow:**
   - Check that "Generate Video (Hugging Face)" node shows your Space URL
   - Ensure all nodes are connected properly
   - Activate the workflow

### Test Your Setup

1. Click the **"When clicking 'Execute workflow'"** (manual trigger) node
2. Click **"Test workflow"**
3. Watch the execution:
   - ✅ Daily Trigger → Get Google News → Parse RSS → Split Items → Pick Top Story
   - ✅ A4F AI (Script) → Clean AI Output
   - ✅ Generate Video (Hugging Face) → Convert to Binary → Read Video File
4. Check the final output - you should have a `.mp4` file!

---

## 🛠️ How It Works

### The Complete Pipeline

1. **n8n on Render** (Workflow Manager):
   - **Schedule Trigger** fires daily at 8 AM
   - **Get Google News** fetches trending topics via RSS
   - **Parse RSS XML** converts XML to JSON
   - **Split News Items** separates individual stories
   - **Pick Top Story** selects the most recent article
   - **A4F AI (Script)** generates a 35-second YouTube Shorts script using Gemini
   - **Clean AI Output** extracts the JSON (script + search term)

2. **Hugging Face Space** (Video Engine):
   - **Generate Video** endpoint receives script and search term via HTTP POST
   - Downloads AI voice using Edge-TTS
   - Fetches portrait video from Pexels API
   - Combines audio + video + subtitles with FFmpeg
   - Returns the final MP4 video file

3. **Back to n8n**:
   - **Convert to Binary** processes the video file
   - **Read Video File** loads the binary data
   - *(Optional)* Upload to YouTube or other platforms

4. **Neon PostgreSQL**:
   - Saves all workflow configurations permanently
   - Stores credentials securely (encrypted)

---

## 🎨 Customization

### Change AI Voice

Edit `huggingface/app.py` line 44:
```python
communicate = edge_tts.Communicate(text, "en-US-AriaNeural")  # Try different voices
```

[Full list of voices](https://speech.microsoft.com/portal/voicegallery)

> **Note:** After changing the Space files, commit and push to Hugging Face to rebuild the Space.

### Change Video Quality

Edit `huggingface/app.py` around line 133:
```python
"-preset", "medium",  # Options: ultrafast, fast, medium, slow
"-crf", "20",         # Lower = better quality (18-28 range)
```

### Schedule Times

Edit the Cron expression in the "Daily Trigger (8 AM)" node in n8n:
- Daily at 8 AM: `0 8 * * *`
- Every 2 hours: `0 */2 * * *`
- Twice daily (8 AM & 8 PM): `0 8,20 * * *`

---

## ⚠️ Important Notes

### Free Tier Limitations

**Render:**
- **Sleep After 15 Minutes:** Your n8n instance will sleep if inactive
- **Solution:** Use [UptimeRobot](https://uptimerobot.com) (free) to ping every 10 minutes:
  ```
  https://your-app-name.onrender.com/healthz
  ```

**Hugging Face Spaces:**
- **Sleep Policy:** Spaces sleep after 48 hours of inactivity
- **Wake-up Time:** ~30 seconds on first request (cold start)
- **Concurrent Requests:** 1 video at a time on free tier

### Storage Behavior

- **Workflows & Credentials:** Stored permanently in Neon PostgreSQL ✅
- **Generated Videos in Hugging Face:** Stored in `/app/output` (ephemeral) ⚠️
- **Solution:** Always download/upload videos within the same workflow execution

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

### "Connection refused to Hugging Face Space"

❌ **Problem:** Space is sleeping or not yet built

✅ **Solution:**
- Check your Space status - it should show "Running"
- Visit the Space URL in a browser to wake it up
- Wait 30 seconds for cold start, then retry

### "PEXELS_API_KEY not set" error from Hugging Face

❌ **Problem:** Secret not configured in Space

✅ **Solution:**
- Go to Space Settings → Variables and secrets
- Verify the secret is named exactly `PEXELS_API_KEY`
- Restart the Space after adding the secret

### "500 Error" from Hugging Face endpoint

❌ **Problem:** FFmpeg error or API issue

✅ **Solution:**
- Check the Space **Logs** tab for specific error messages
- Try a different search term (more generic like "ocean", "city")
- Verify Pexels API key is valid

### Workflow Not Triggering

❌ **Problem:** n8n instance is asleep

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
