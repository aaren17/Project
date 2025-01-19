from flask import Flask, jsonify
import yt_dlp
import os

app = Flask(__name__)

# YouTube Live URL
YOUTUBE_URL = "https://youtu.be/3LXQWU67Ufk"
COOKIES_FILE = "cookies.txt"  # Path to your YouTube cookies file

# Ensure cookies file exists
if not os.path.exists(COOKIES_FILE):
    raise FileNotFoundError(f"Cookies file '{COOKIES_FILE}' not found. Please place it in the same directory as this script.")

def get_youtube_hls_stream(youtube_url):
    """Get the HLS playlist URL from YouTube."""
    ydl_opts = {
        "format": "best",
        "quiet": True,
        "cookiefile": COOKIES_FILE,  # Use the cookies file to handle restricted videos
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            return info.get("url")
    except yt_dlp.utils.DownloadError as e:
        raise yt_dlp.utils.DownloadError(f"Failed to fetch HLS URL. {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")

@app.route('/video')
def stream_hls_video():
    """Serve HLS video directly from YouTube."""
    try:
        hls_url = get_youtube_hls_stream(YOUTUBE_URL)
        return jsonify({'hls_url': hls_url})
    except yt_dlp.utils.DownloadError as e:
        return jsonify({'error': 'Failed to fetch HLS URL. Make sure the video is accessible.', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500

@app.route('/anomalies')
def fetch_anomalies():
    """Return mock anomaly data."""
    anomalies = [
        {"description": "Unauthorized access detected", "timestamp": "2025-01-19T11:07:00"},
        {"description": "Motion detected near entrance", "timestamp": "2025-01-19T11:08:30"},
    ]
    return jsonify(anomalies)

@app.route('/debug-cookies')
def debug_cookies():
    """Check if cookies file exists and is accessible."""
    if os.path.exists(COOKIES_FILE):
        return jsonify({'status': 'Cookies file found and accessible.'})
    return jsonify({'status': 'Cookies file is missing!'}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
