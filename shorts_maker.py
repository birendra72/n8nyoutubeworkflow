#!/usr/bin/env python3
"""
Low-Resource Video Automation Engine for Render Free Tier
Target: 512MB RAM, 0.1 CPU
Output: 720x1280 (HD Ready) vertical videos with AI voice
"""

import os
import sys
import gc
import requests
import subprocess
import asyncio
import edge_tts
from pathlib import Path

# === CONFIGURATION ===
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "YOUR_PEXELS_KEY_HERE")
OUTPUT_DIR = "/home/node/output"
TEMP_DIR = "/home/node/temp"

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

def log(message):
    """Simple logging to stderr for n8n visibility"""
    print(f"[shorts_maker] {message}", file=sys.stderr, flush=True)

async def generate_voice(text, voice="en-US-ChristopherNeural"):
    """
    Generate AI voice using Edge-TTS
    Returns: (audio_path, duration_seconds)
    Memory-safe: Streams directly to file
    """
    log(f"Generating voice for text: {text[:50]}...")
    
    audio_path = os.path.join(TEMP_DIR, "voice.mp3")
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(audio_path)
        
        # Get audio duration using ffprobe
        duration = get_media_duration(audio_path)
        log(f"Voice generated: {audio_path} ({duration:.2f}s)")
        
        return audio_path, duration
    except Exception as e:
        log(f"ERROR generating voice: {e}")
        raise

def get_media_duration(file_path):
    """Get duration of audio/video file using ffprobe"""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def download_pexels_videos(query, target_duration):
    """
    Download vertical videos from Pexels API
    Memory-safe: Streams download to disk, not to memory
    Returns: list of video file paths
    """
    log(f"Searching Pexels for: '{query}'")
    
    if PEXELS_API_KEY == "YOUR_PEXELS_KEY_HERE":
        log("ERROR: PEXELS_API_KEY not set!")
        sys.exit(1)
    
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=3&size=medium"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        log(f"ERROR fetching Pexels API: {e}")
        sys.exit(1)
    
    if not data.get('videos'):
        log(f"ERROR: No videos found for '{query}'")
        sys.exit(1)
    
    video_paths = []
    total_downloaded = 0
    
    # Download videos until we have enough duration
    for i, video in enumerate(data['videos'][:3]):  # Max 3 clips
        # Get the HD file (closest to 720p width to save bandwidth)
        video_files = video['video_files']
        best_file = min(
            [vf for vf in video_files if vf.get('width', 0) > 0],
            key=lambda x: abs(x.get('width', 1920) - 720)
        )
        
        video_url = best_file['link']
        video_path = os.path.join(TEMP_DIR, f"clip_{i}.mp4")
        
        log(f"Downloading clip {i+1}/3...")
        
        # CRITICAL: Stream download to disk (DO NOT load into memory)
        try:
            with requests.get(video_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(video_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            video_paths.append(video_path)
            total_downloaded += 1
            
            # Memory cleanup
            del r
            gc.collect()
            
        except Exception as e:
            log(f"WARNING: Failed to download clip {i+1}: {e}")
            continue
    
    if not video_paths:
        log("ERROR: Could not download any videos")
        sys.exit(1)
    
    log(f"Downloaded {total_downloaded} clips")
    return video_paths

def create_video(audio_path, video_clips, output_path):
    """
    Combine audio and video using FFmpeg
    OPTIMIZED FOR 512MB RAM:
    - Resolution: 720x1280 (not 1080p)
    - Preset: ultrafast
    - Threads: 2
    - Audio: 44.1kHz
    """
    log("Creating final video with FFmpeg...")
    
    # Create concat file for FFmpeg
    concat_file = os.path.join(TEMP_DIR, "concat.txt")
    with open(concat_file, 'w') as f:
        for clip in video_clips:
            # Escape path for FFmpeg
            escaped = clip.replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")
    
    # FFmpeg command optimized for low resources
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,  # Video input (concatenated)
        "-i", audio_path,   # Audio input
        
        # Video filters: Scale to 720x1280 and crop
        "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
        
        # Video codec settings (OPTIMIZED FOR LOW RAM)
        "-c:v", "libx264",
        "-preset", "ultrafast",  # CRITICAL: Trades quality for speed/memory
        "-threads", "2",         # CRITICAL: Limit CPU threads
        "-crf", "28",           # Quality (higher = smaller file)
        
        # Audio codec settings
        "-c:a", "aac",
        "-ar", "44100",         # 44.1kHz (not 48kHz to save buffer)
        "-b:a", "128k",
        
        # Timing: Stop when audio ends
        "-shortest",
        
        # Map streams explicitly
        "-map", "0:v:0",
        "-map", "1:a:0",
        
        # Output
        output_path
    ]
    
    try:
        log(f"Running FFmpeg (this may take 30-60 seconds)...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode != 0:
            log(f"FFmpeg ERROR: {result.stderr}")
            sys.exit(1)
        
        log(f"Video created successfully: {output_path}")
        
        # Verify output exists
        if not os.path.exists(output_path):
            log("ERROR: Output file was not created!")
            sys.exit(1)
        
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        log(f"Output size: {file_size_mb:.2f} MB")
        
    except subprocess.TimeoutExpired:
        log("ERROR: FFmpeg timeout (video too long or system overloaded)")
        sys.exit(1)
    except Exception as e:
        log(f"ERROR during video creation: {e}")
        sys.exit(1)

def cleanup_temp_files():
    """Remove temporary files to free up disk space"""
    try:
        for file in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        log("Temp files cleaned up")
    except Exception as e:
        log(f"WARNING: Could not clean temp files: {e}")

async def main():
    """Main execution flow"""
    if len(sys.argv) < 3:
        print("Usage: python3 shorts_maker.py \"<script_text>\" \"<search_term>\"", file=sys.stderr)
        sys.exit(1)
    
    script_text = sys.argv[1]
    search_term = sys.argv[2]
    
    log("=" * 50)
    log("LOW-RESOURCE VIDEO AUTOMATION ENGINE")
    log("=" * 50)
    log(f"Script: {script_text[:60]}...")
    log(f"Search: {search_term}")
    log("=" * 50)
    
    try:
        # Step 1: Generate voice (memory-safe)
        audio_path, audio_duration = await generate_voice(script_text)
        
        # Step 2: Download videos (streaming to disk)
        video_clips = download_pexels_videos(search_term, audio_duration)
        
        # Memory cleanup before heavy FFmpeg operation
        gc.collect()
        
        # Step 3: Render final video (optimized for 512MB RAM)
        output_filename = f"short_{os.getpid()}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        create_video(audio_path, video_clips, output_path)
        
        # Step 4: Cleanup temp files
        cleanup_temp_files()
        
        # SUCCESS: Print ONLY the output path to stdout (for n8n)
        print(output_path)
        log("SUCCESS!")
        sys.exit(0)
        
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())