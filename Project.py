from flask import Flask, jsonify
import yt_dlp

app = Flask(__name__)

# YouTube Live URL
YOUTUBE_URL = "https://youtu.be/3LXQWU67Ufk"
COOKIES_FILE = "cookies.txt"  # Path to your YouTube cookies file (if required)

def get_youtube_hls_stream(youtube_url):
    """Get the HLS playlist URL from YouTube."""
    ydl_opts = {
        "format": "best",
        "quiet": True,
        "cookiefile": COOKIES_FILE,  # Add cookies file to handle restricted videos
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info.get("url")

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
