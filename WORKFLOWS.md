# n8n Workflow Files

This directory contains ready-to-import n8n workflows for YouTube Shorts automation.

## Available Workflows

### 1. `workflow-simple-test.json` (⭐ Start Here)

**Purpose:** Test workflow to verify your setup works

**Features:**
- Manual trigger (click to run)
- Hardcoded test script and search term
- Generates a single video
- No external dependencies

**Import Steps:**
1. Open n8n
2. Click **"Add workflow"** → **"Import from File"**
3. Select `workflow-simple-test.json`
4. Click **"Execute Workflow"** to test

**Expected Result:**
- Video generated in `/home/node/output/`
- Output shows file path and success status

---

### 2. `workflow-automated-trends.json` (Advanced)

**Purpose:** Fully automated daily YouTube Shorts from Google Trends

**Features:**
- Runs daily at 8:00 AM
- Fetches trending topics from Google Trends
- Creates video about random trend
- Uploads to YouTube automatically

**Requirements:**
- YouTube OAuth2 credentials configured in n8n
- `N8N_RUNNERS_DISABLED=true` environment variable

**Import Steps:**
1. Import workflow
2. Open **"Upload to YouTube"** node
3. Click on **credentials** field
4. Add your YouTube OAuth2 API credentials
5. Save workflow
6. Activate workflow (toggle in top-right)

---

## How to Import Workflows

### Method 1: Import from File (Recommended)
1. Download the `.json` file to your computer
2. In n8n, click **"+"** → **"Import from File"**
3. Select the workflow file
4. Click **"Import"**

### Method 2: Copy-Paste JSON
1. Open the `.json` file in a text editor
2. Copy all contents
3. In n8n, click **"+"** → **"Import from URL or File"**
4. Paste JSON into the text area
5. Click **"Import"**

---

## Testing the Simple Workflow

1. **Import** `workflow-simple-test.json`
2. **Click "Execute Workflow"** button (top-right)
3. **Wait 30-60 seconds** for video generation
4. **Check Output Summary node** for success status
   - `video_path`: Path to generated video
   - `status`: "success"
   - `script`: Text that was narrated
   - `search_term`: Video search query used

---

## Customizing Workflows

### Change Script Content (Simple Test)

Edit the **"Set Input Data"** node:
```json
{
  "script": "Your custom narration text here",
  "search_term": "ocean sunset"
}
```

### Change Schedule (Automated)

Edit the **"Daily 8 AM Trigger"** node:
- Daily at 8 AM: `0 8 * * *`
- Every 2 hours: `0 */2 * * *`
- Twice daily (8 AM & 8 PM): `0 8,20 * * *`

### Change Trend Source

Edit the **"Get Google Trends"** node URL:
- US Trends: `https://trends.google.com/trending/rss?geo=US`
- India Trends: `https://trends.google.com/trending/rss?geo=IN`
- UK Trends: `https://trends.google.com/trending/rss?geo=GB`

---

## Troubleshooting

### Error: "Virtual environment is missing"

**Solution:** Add to Render environment variables:
```
N8N_RUNNERS_DISABLED=true
```
Then restart service.

### Error: "PEXELS_API_KEY not set"

**Solution:** Add Pexels API key to Render:
```
PEXELS_API_KEY=your_actual_key_here
```

### Error: "YouTube upload failed"

**Check:**
1. YouTube OAuth2 credentials are configured
2. Credentials have upload permissions
3. Video file size < 128MB
4. YouTube API quota not exceeded

### Video Generation Times Out

**Cause:** Text too long or server overloaded

**Solution:**
- Reduce script text length (< 200 words)
- Check Render logs for memory issues

---

## YouTube API Setup (For Automated Workflow)

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

## Next Steps

1. ✅ **Test:** Import `workflow-simple-test.json` and run once
2. ✅ **Verify:** Check output video path and file
3. ✅ **Customize:** Edit script and search terms
4. ✅ **Automate:** Import `workflow-automated-trends.json`
5. ✅ **Schedule:** Set up daily automation
6. ✅ **Upload:** Configure YouTube API for automatic uploads

---

**Need Help?** Check:
- [N8N_WORKFLOW_GUIDE.md](./N8N_WORKFLOW_GUIDE.md) - Detailed workflow setup
- [README.md](./README.md) - Full deployment guide
- [DEPLOY.md](./DEPLOY.md) - Quick deployment reference
