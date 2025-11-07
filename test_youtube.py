#!/usr/bin/env python3
"""
Test script to verify YouTube extraction works
"""
import yt_dlp
import sys

def test_youtube_extraction(url):
    """Test if we can extract info from a YouTube URL"""
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android'],
                'skip': ['hls', 'dash'],
            }
        },
    }
    
    try:
        print(f"Testing URL: {url}")
        print("Extracting info with Android client...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:
                info = info['entries'][0]
            
            print("\n✅ SUCCESS!")
            print(f"Title: {info.get('title', 'Unknown')}")
            print(f"Duration: {info.get('duration', 0)} seconds")
            print(f"Has audio URL: {'url' in info or 'formats' in info}")
            
            if 'formats' in info:
                audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none']
                print(f"Audio formats available: {len(audio_formats)}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ FAILED!")
        print(f"Error: {e}")
        
        if "Sign in to confirm" in str(e) or "bot" in str(e).lower():
            print("\nThis video is blocked by YouTube.")
            print("Try a different video (non-age-restricted, non-live stream)")
        
        return False


if __name__ == "__main__":
    # Test URLs
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - should work
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo - should work
    ]
    
    if len(sys.argv) > 1:
        # Test user-provided URL
        test_urls = [sys.argv[1]]
    
    print("=" * 60)
    print("YouTube Extraction Test")
    print("=" * 60)
    
    for url in test_urls:
        print()
        success = test_youtube_extraction(url)
        print("-" * 60)
        
        if not success:
            print("\n⚠️  Some videos may not work due to YouTube restrictions.")
            print("Try using regular uploaded videos (not live streams or age-restricted)")

