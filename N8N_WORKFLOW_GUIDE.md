# n8n Workflow Setup Guide

## Environment Variables Required

Add this to your Render environment variables:

```
N8N_RUNNERS_DISABLED=true
```

This disables n8n's Python task runner requirement, allowing Execute Command to work.

## Workflow Configuration

### Node 1: Schedule Trigger (or Manual Trigger for Testing)
- **Type:** Schedule / Manual
- **Schedule (if using):** `0 8 * * *` (8:00 AM daily)

### Node 2: Set Input Data
- **Node Type:** Set
- **Mode:** Manual Mapping
- **Fields:**

| Field Name | Value |
|------------|-------|
| `script` | This is a test of the emergency broadcast system. |
| `search_term` | nature |

### Node 3: Execute Command
- **Node Type:** Execute Command
- **Command:** `python3`
- **Arguments (click "Add Argument" for each):**

```
Argument 1: /home/node/shorts_maker.py
Argument 2: {{ $json.script }}
Argument 3: {{ $json.search_term }}
```

**IMPORTANT:** Use the "Arguments" field, NOT "Command with arguments"

### Node 4: Read Binary File (After Video is Created)
- **Node Type:** Read Binary Files
- **File Selector:** Single File Path
- **File Path:** Extract from Execute Command output (see below)

## Expected Output

### Execute Command Node Output (stdout):
```
/home/node/output/short_12345.mp4
```

### Execute Command Node Logs (stderr):
```
[shorts_maker] Generating voice for text: This is a test...
[shorts_maker] Voice generated: /home/node/temp/voice.mp3 (8.50s)
[shorts_maker] Searching Pexels for: 'nature'
[shorts_maker] Downloaded 3 clips
[shorts_maker] Creating final video with FFmpeg...
[shorts_maker] Running FFmpeg (this may take 30-60 seconds)...
[shorts_maker] Video created successfully: /home/node/output/short_12345.mp4
[shorts_maker] Output size: 8.25 MB
[shorts_maker] Temp files cleaned up
[shorts_maker] SUCCESS!
```

## Troubleshooting

### Error: "Python runner unavailable: Virtual environment is missing"

**Cause:** You're using the Code node instead of Execute Command, or N8N_RUNNERS_DISABLED is not set.

**Solution:**
1. Add `N8N_RUNNERS_DISABLED=true` to Render environment variables
2. Redeploy the service
3. Use Execute Command node, NOT Code node

### Error: "PEXELS_API_KEY not set"

**Solution:** Add your Pexels API key to Render environment variables:
```
PEXELS_API_KEY=your_actual_key_here
```

### Error: "permission denied"

**Solution:** Make sure the script path is exact:
```
/home/node/shorts_maker.py
```

### Video Generation Takes Too Long

**Expected:** 30-60 seconds for a 30-second clip  
**If longer:** Check Render logs for memory issues

## Testing Workflow

1. Create a simple workflow with Manual Trigger
2. Add Set node with test data
3. Add Execute Command node with Python script
4. Click "Execute Workflow"
5. Check output in Execute Command node

## Render Environment Variables Checklist

- [ ] `N8N_BASIC_AUTH_ACTIVE=true`
- [ ] `N8N_BASIC_AUTH_USER=admin`
- [ ] `N8N_BASIC_AUTH_PASSWORD=<your_password>`
- [ ] `N8N_RUNNERS_DISABLED=true` ⭐ **NEW - CRITICAL**
- [ ] `PEXELS_API_KEY=<your_key>`
- [ ] `WEBHOOK_URL=https://your-app.onrender.com`
- [ ] `GENERIC_TIMEZONE=Asia/Kolkata` (optional)

After adding `N8N_RUNNERS_DISABLED=true`, click "Manual Deploy" in Render to restart the service.
