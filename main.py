from flask import Flask, request, jsonify, send_from_directory
import os
from app import downloadVideo, output_folder

app = Flask(__name__)

# Ensure output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

@app.route('/')
def index():
    return jsonify({
        "message": "Facebook Video Downloader API is running!",
        "endpoints": {
            "/download": "POST with {'url': 'FB_VIDEO_URL'}",
            "/files/<filename>": "GET to download specific file"
        }
    })

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400
    
    video_url = data['url']
    print(f"Processing URL: {video_url}")
    
    result = downloadVideo(video_url)
    
    if result.get("status") == "success":
        # Construct a download link for the client
        download_url = f"{request.host_url}files/{result['filename']}"
        return jsonify({
            "status": "success",
            "video_id": result['video_id'],
            "filename": result['filename'],
            "download_url": download_url
        })
    else:
        return jsonify({
            "status": "error",
            "message": result.get("message", "Unknown error occurred")
        }), 500

@app.route('/files/<path:filename>')
def serve_file(filename):
    return send_from_directory(output_folder, filename)

if __name__ == '__main__':
    # Railway provides the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
