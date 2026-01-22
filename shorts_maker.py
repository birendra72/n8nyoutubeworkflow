import os
import sys
import requests
import random
import subprocess
import asyncio
import edge_tts

# --- CONFIGURATION ---
# It is best practice to pass the API Key from n8n via Environment Variable
# But you can hardcode it here if you prefer (not recommended for public repos)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "YOUR_PEXELS_KEY_HERE") 

OUTPUT_DIR = "/home/node/output"
TEMP_DIR = "/home/node/temp"

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

async def generate_voice(text, voice="en-US-ChristopherNeural"):
    """
    Generates MP3 and SRT (Subtitles) from text using Edge-TTS.
    We need SRT for FFmpeg to burn subtitles into the video.
    """
    print(f"Generating Audio for: {text[:30]}...")
    communicate = edge_tts.Communicate(text, voice)
    audio_path = os.path.join(TEMP_DIR, "audio.mp3")
    sub_path = os.path.join(TEMP_DIR, "subs.srt")
    
    # Generate Audio file
    await communicate.save(audio_path)
    
    # Generate Subtitles
    # Note: We run the stream again to calculate timing for subtitles
    submaker = edge_tts.SubMaker()
    async for chunk in communicate.stream():
        if chunk["type"] == "WordBoundary":
            submaker.feed(chunk)
    
    with open(sub_path, "w", encoding="utf-8") as file:
        file.write(submaker.get_srt())
        
    return audio_path, sub_path

def download_stock_footage(query):
    """Downloads vertical videos from Pexels API"""
    print(f"Searching Pexels for: {query}")
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=3"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error connecting to Pexels: {e}")
        return []
    
    video_paths = []
    if 'videos' not in data or not data['videos']:
        print("No videos found.")
        return []

    for i, video in enumerate(data['videos']):
        # Get the video file that is closest to 720p/1080p width to save bandwidth
        # Pexels returns multiple sizes. We look for one with width ~1080
        video_files = video['video_files']
        best_file = min(video_files, key=lambda x: abs(x['width'] - 1080))
        link = best_file['link']
        
        vid_path = os.path.join(TEMP_DIR, f"clip_{i}.mp4")
        with open(vid_path, 'wb') as f:
            f.write(requests.get(link).content)
        video_paths.append(vid_path)
        
    return video_paths

def get_audio_duration(audio_path):
    """Uses ffprobe to get exact duration of audio"""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

def render_video(audio_path, video_paths, sub_path, output_file):
    """
    Stitches video clips, adds audio, and burns subtitles.
    """
    print("Rendering video...")
    
    # 1. Prepare input list for FFmpeg
    # We loop the downloaded clips until they match the audio length
    list_path = os.path.join(TEMP_DIR, "files.txt")
    audio_duration = get_audio_duration(audio_path)
    current_duration = 0
    
    with open(list_path, 'w') as f:
        while current_duration < audio_duration + 5: # Buffer 5 seconds
            for vid in video_paths:
                # Escape single quotes for ffmpeg concat safe file
                abs_path = os.path.abspath(vid).replace("'", "'\\''")
                f.write(f"file '{abs_path}'\n")
                current_duration += 4 # Assume avg clip useful duration is 4s
    
    # 2. Escape path for subtitles filter (FFmpeg assumes ':' is a separator)
    # On Linux, simple path usually works, but escaping is safer
    sub_path_escaped = sub_path.replace(":", "\\:")

    # 3. FFmpeg Command
    # -safe 0: Allow absolute paths
    # -vf: Video Filter (Crop to 9:16, Scale, Subtitles)
    # -shortest: Stop when audio stops
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", list_path,
        "-i", audio_path,
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:-1:-1,subtitles={sub_path_escaped}:force_style='FontName=Arial,FontSize=20,PrimaryColour=&H00FFFF,BackColour=&H80000000,BorderStyle=3,Outline=1,Shadow=0,Alignment=2,MarginV=50'",
        "-c:v", "libx264", "-preset", "ultrafast", # Ultrafast for speed on free CPU
        "-c:a", "aac",
        "-map", "0:v", "-map", "1:a",
        "-shortest",
        output_file
    ]
    
    subprocess.run(cmd, check=True)
    print(f"SUCCESS:{output_file}")

if __name__ == "__main__":
    # Expecting: python shorts_maker.py "My Script" "Search Query"
    if len(sys.argv) < 3:
        print("Usage: python shorts_maker.py <script> <search_term>")
        sys.exit(1)
        
    script_text = sys.argv[1]
    search_query = sys.argv[2]
    
    # 1. Generate Audio & Subs
    audio, subs = asyncio.run(generate_voice(script_text))
    
    # 2. Download Content
    videos = download_stock_footage(search_query)
    
    # 3. Render
    if videos:
        output_filename = os.path.join(OUTPUT_DIR, f"final_{random.randint(1000,9999)}.mp4")
        try:
            render_video(audio, videos, subs, output_filename)
            # Output the path cleanly so n8n can capture it
            print(output_filename) 
        except Exception as e:
            print(f"Error during rendering: {e}")
            sys.exit(1)
    else:
        print("Error: Could not find video footage.")
        sys.exit(1)