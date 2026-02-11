import os
import uuid
import shutil
import tempfile
from flask import Flask, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)

@app.route("/download", methods=["POST"])
def download_reel():
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    reel_url = data["url"]

    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    unique_id = str(uuid.uuid4())
    output_path = os.path.join(temp_dir, f"{unique_id}.mp4")

    ydl_opts = {
        "format": "best",
        "outtmpl": output_path,
        "quiet": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([reel_url])

        return send_file(
            output_path,
            as_attachment=True,
            download_name="facebook_reel.mp4",
            mimetype="video/mp4"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Cleanup temp directory
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
