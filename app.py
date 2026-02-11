import requests
import json
import subprocess
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Enable CORS for all routes
output_folder = "Output"

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "FB Downloader API is running"}), 200

@app.route('/favicon.ico')
def favicon():
    return '', 204

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

def downloadFile(link, file_name):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    try:
        resp = requests.get(link, headers=headers).content
    except Exception as e:
        print(f"Failed to open {link}: {e}")
        return False
    with open(os.path.join(output_folder, file_name), 'wb') as f:
        f.write(resp)
    return True

def process_video(link):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Dnt': '1',
        'Dpr': '1.3125',
        'Priority': 'u=0, i',
        'Sec-Ch-Prefers-Color-Scheme': 'dark',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'Sec-Ch-Ua-Full-Version-List': '"Chromium";v="124.0.6367.156", "Google Chrome";v="124.0.6367.156", "Not-A.Brand";v="99.0.0.0"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Model': '""',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Ch-Ua-Platform-Version': '"15.0.0"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Viewport-Width': '1463'
    }
    try:
        resp = requests.get(link, headers=headers)
    except Exception as e:
        return {"error": f"Failed to open link: {e}"}
    
    link = resp.url.split('?')[0]
    html_content = resp.text
    splits = link.split('/')
    video_id = ''
    for ids in splits:
        if ids.isdigit():
            video_id = ids
    
    if not video_id:
        return {"error": "Could not extract video ID from URL"}

    try:
        try:
            target_video_audio_id = html_content.split('"id":"{}"'.format(video_id))[1].split(
                '"dash_prefetch_experimental":[')[1].split(']')[0].strip()
        except:
            target_video_audio_id = html_content.split('"video_id":"{}"'.format(video_id))[1].split(
                '"dash_prefetch_experimental":[')[1].split(']')[0].strip()
        
        list_str = "[{}]".format(target_video_audio_id)
        sources = json.loads(list_str)
        
        video_link = html_content.split('"representation_id":"{}"'.format(sources[0]))[1].split('"base_url":"')[1].split('"')[0]
        video_link = video_link.replace('\\', '')
        
        audio_link = html_content.split('"representation_id":"{}"'.format(sources[1]))[1].split('"base_url":"')[1].split('"')[0]
        audio_link = audio_link.replace('\\', '')
        
        # Download files
        video_temp = f'video_{video_id}.mp4'
        audio_temp = f'audio_{video_id}.mp4'
        
        if not downloadFile(video_link, video_temp):
            return {"error": "Failed to download video stream"}
        if not downloadFile(audio_link, audio_temp):
            return {"error": "Failed to download audio stream"}
        
        video_path = os.path.join(output_folder, video_temp)
        audio_path = os.path.join(output_folder, audio_temp)
        combined_file_name = f'merged_{video_id}.mp4'
        combined_file_path = os.path.join(output_folder, combined_file_name)
        
        cmd = f'ffmpeg -hide_banner -loglevel error -i "{video_path}" -i "{audio_path}" -c copy "{combined_file_path}"'
        subprocess.call(cmd, shell=True)
        
        if os.path.exists(combined_file_path):
            if os.path.exists(video_path): os.remove(video_path)
            if os.path.exists(audio_path): os.remove(audio_path)
            
            final_output_path = os.path.join(output_folder, f'{video_id}.mp4')
            if os.path.exists(final_output_path):
                os.remove(final_output_path)
            os.rename(combined_file_path, final_output_path)
            
            return {"success": True, "video_id": video_id, "file_path": final_output_path}
        else:
            return {"error": "FFmpeg merging failed"}
            
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400
    
    url = data['url']
    result = process_video(url)
    
    if "error" in result:
        return jsonify(result), 500
    
    # Return the binary file directly
    file_path = result['file_path']
    video_id = result['video_id']
    
    return send_file(
        file_path, 
        as_attachment=True, 
        download_name=f"{video_id}.mp4",
        mimetype='video/mp4'
    )

@app.route('/get_video/<video_id>', methods=['GET'])
def get_video(video_id):
    file_path = os.path.join(output_folder, f'{video_id}.mp4')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
