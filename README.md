# n8n YouTube Shorts Automation 🎥

Automate YouTube Shorts creation with AI voice narration and background videos using n8n workflows on Render's free tier.

## 🌟 Features

- **Custom n8n Docker Image** with Python and FFmpeg pre-installed
- **AI Voice Generation** using Microsoft Edge TTS
- **Automated Video Creation** with background footage
- **Free Deployment** on Render
- **Scheduled Automation** via n8n workflows

## 📋 Prerequisites

- GitHub account (to host this repository)
- [Render](https://render.com) account (free tier)
- [Pexels API Key](https://www.pexels.com/api/) (free, for stock videos)

## 🚀 Quick Start

### Step 1: Deploy to Render

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

7. **Environment Variables** (Add these in Render):
   
   **Required Variables:**
   ```
   N8N_BASIC_AUTH_ACTIVE=true
   N8N_BASIC_AUTH_USER=admin
   N8N_BASIC_AUTH_PASSWORD=YourSecurePassword123!
   PEXELS_API_KEY=your_pexels_api_key_here
   WEBHOOK_URL=https://your-app-name.onrender.com
   ```
   
   **Optional Variables (Recommended):**
   ```
   GENERIC_TIMEZONE=Asia/Kolkata
   EXECUTIONS_TIMEOUT=3600
   N8N_CONCURRENCY_PRODUCTION_LIMIT=1
   ```
   
   > **Get Your Pexels API Key:**
   > 1. Go to https://www.pexels.com/api/
   > 2. Sign up for free
   > 3. Copy your API key
   > 4. Paste it in Render's environment variables

8. Click **Create Web Service**

9. Wait for deployment (first build takes 5-10 minutes)

### Step 2: Access n8n

1. Once deployed, your n8n instance will be available at:
   ```
   https://your-app-name.onrender.com
   ```

2. Log in with the credentials you set in environment variables

### Step 3: Create Your First Workflow

1. In n8n, create a new workflow

2. Add the following nodes:

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

3. **Activate** the workflow

## 🎬 How It Works

1. **Scheduled Trigger** fires at your specified time
2. **Script Data** defines the narration text and video search term
3. **Execute Command** runs the Python script that:
   - Generates AI voice using Edge-TTS
   - Downloads background video from Pexels
   - Combines audio + video with FFmpeg
   - Outputs final video to `/tmp/final_short.mp4`
4. **Read Binary File** loads the generated video
5. **Upload** (optional) to YouTube or other platforms

## 🛠️ Customization

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

Edit FFmpeg parameters in `shorts_maker.py` line 100-101 for resolution/bitrate

## ⚠️ Important Notes

### Render Free Tier Limitations

- **Sleep After 15 Minutes:** Your n8n instance will sleep if inactive
- **Solution:** Use [UptimeRobot](https://uptimerobot.com) (free) to ping your n8n health endpoint every 10 minutes:
  ```
  https://your-app-name.onrender.com/healthz
  ```

### Storage

- Render's free tier has ephemeral storage
- Generated videos are stored in `/tmp` and will be lost on restart
- **Solution:** Always upload/download videos within the same workflow execution

## 🐛 Troubleshooting

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

## 📚 Resources

- [n8n Documentation](https://docs.n8n.io/)
- [Render Documentation](https://render.com/docs)
- [Pexels API Docs](https://www.pexels.com/api/documentation/)
- [Edge-TTS Voices](https://github.com/rany2/edge-tts)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

## 📺 Video Tutorial

For a step-by-step visual guide on deploying custom Docker apps on Render:
- [Deploy n8n with FFmpeg on Render](https://www.youtube.com/watch?v=ciDzX398pl0)

## 📝 License

MIT License - Feel free to modify and use for your projects!

## 🤝 Contributing

Issues and pull requests are welcome! Feel free to improve the script or documentation.

---

**Made with ❤️ for automated content creation**
