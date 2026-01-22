#!/usr/bin/env python3
"""
YouTube Shorts Automation Script
Generates AI voice narration and combines it with background video
Usage: python3 shorts_maker.py "script text" "search_term"
"""

import sys
import os
import asyncio
import subprocess
import tempfile
import requests
from pathlib import Path

async def generate_voice(text, output_file):
    """Generate AI voice using edge-tts"""
    import edge_tts
    
    # Use a natural-sounding voice (you can change this)
    voice = "en-US-AriaNeural"
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    print(f"✓ Voice generated: {output_file}")

def download_background_video(search_term, output_file):
    """
    Download a background video based on search term
    This is a placeholder - you'll need to integrate with a video API
    For now, we'll use a stock video URL or Pexels API
    """
    # You can use Pexels API (free) for stock videos
    # Sign up at https://www.pexels.com/api/ to get an API key
    # For this example, we'll download a sample video
    
    # Pexels API integration (you need to add your API key)
    PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', 'YOUR_API_KEY_HERE')
    
    if PEXELS_API_KEY == 'YOUR_API_KEY_HERE':
        print("⚠ Warning: No Pexels API key set. Using placeholder video.")
        print("Set PEXELS_API_KEY environment variable in n8n for video search.")
        # Download a sample video (you can host one or use a direct URL)
        sample_url = "https://www.w3schools.com/html/mov_bbb.mp4"
        download_video_from_url(sample_url, output_file)
    else:
        # Search for videos on Pexels
        headers = {"Authorization": PEXELS_API_KEY}
        url = f"https://api.pexels.com/videos/search?query={search_term}&per_page=1&orientation=portrait"
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['videos']:
                video_files = data['videos'][0]['video_files']
                # Get portrait HD video
                portrait_video = next(
                    (v for v in video_files if v.get('width', 0) <= 1080 and v.get('height', 0) >= 1920),
                    video_files[0]
                )
                video_url = portrait_video['link']
                download_video_from_url(video_url, output_file)
            else:
                print(f"✗ No videos found for '{search_term}'")
                sys.exit(1)
        else:
            print(f"✗ Pexels API error: {response.status_code}")
            sys.exit(1)

def download_video_from_url(url, output_file):
    """Download video from URL"""
    print(f"⏬ Downloading video...")
    response = requests.get(url, stream=True)
    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✓ Video downloaded: {output_file}")

def combine_audio_video(video_file, audio_file, output_file):
    """Combine audio and video using FFmpeg"""
    print(f"🎬 Combining audio and video...")
    
    # FFmpeg command to combine video and audio
    # - Loop video if audio is longer
    # - Crop to 9:16 aspect ratio (1080x1920)
    # - Add fade in/out effects
    cmd = [
        'ffmpeg',
        '-stream_loop', '-1',  # Loop video
        '-i', video_file,
        '-i', audio_file,
        '-t', '60',  # Max 60 seconds (YouTube Shorts limit)
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',  # End when shortest stream ends
        '-y',  # Overwrite output file
        output_file
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Final video created: {output_file}")
    else:
        print(f"✗ FFmpeg error: {result.stderr}")
        sys.exit(1)

async def main():
    if len(sys.argv) < 3:
        print("Usage: python3 shorts_maker.py \"script text\" \"search_term\"")
        sys.exit(1)
    
    script_text = sys.argv[1]
    search_term = sys.argv[2]
    
    print("=" * 50)
    print("🎥 YouTube Shorts Generator")
    print("=" * 50)
    print(f"Script: {script_text[:50]}...")
    print(f"Search: {search_term}")
    print("=" * 50)
    
    # Create temporary directory for intermediate files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # File paths
        audio_file = os.path.join(temp_dir, "voice.mp3")
        video_file = os.path.join(temp_dir, "background.mp4")
        output_file = "/tmp/final_short.mp4"
        
        # Step 1: Generate AI voice
        print("\n[1/3] Generating AI voice...")
        await generate_voice(script_text, audio_file)
        
        # Step 2: Download background video
        print("\n[2/3] Downloading background video...")
        download_background_video(search_term, video_file)
        
        # Step 3: Combine audio and video
        print("\n[3/3] Creating final video...")
        combine_audio_video(video_file, audio_file, output_file)
        
        print("\n" + "=" * 50)
        print("✓ SUCCESS! Video created at:", output_file)
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Note: In production, you might want to keep temp files for debugging
        # For now, we'll leave them for n8n to handle
        pass

if __name__ == "__main__":
    asyncio.run(main())
