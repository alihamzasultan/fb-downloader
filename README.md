# Facebook Video Downloader Python Script
This script is developed in Python and downloads Facebook videos with audio and merges them using ffmpeg

# URL types allowed:
https://web.facebook.com/rabbids/videos/7350686091725184/<br>
https://www.facebook.com/reel/1234.....<br>
https://www.facebook.com/share/r/abcdef..../

### Flask Server Usage (Deployment)

To run the server locally:
```bash
pip install -r requirements.txt
python main.py
```

### Endpoints

- **POST `/download`**: Send a JSON body with the Facebook URL.
  ```json
  { "url": "https://www.facebook.com/reel/..." }
  ```
- **GET `/files/<filename>`**: Download the resulting video file.

### Railway Deployment

This project is pre-configured for Railway:
- `Procfile`: Tells Railway how to run the app.
- `nixpacks.toml`: Tells Railway to install `ffmpeg`.
- `requirements.txt`: Python dependencies.

# How to setup:
* Install this library using the command on your terminal/command prompt
<pre>pip install requests</pre>
* Unzip the ffmpeg archive into the script folder
* Now, run the script by executing it. Paste the video URL. Let the script do the magic for you!
