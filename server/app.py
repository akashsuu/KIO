import os
import glob
from flask import Flask, jsonify, send_file, render_template_string
from flask_cors import CORS
import socket

app = Flask(__name__)
CORS(app)

# The root directory for the kio_cat animations
# It assumes kio_cat folder is in the parent directory
ANIMATION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'kio_cat'))

def get_animations():
    """Scans the kio_cat directory and returns a dictionary of animations and their frames."""
    animations = {}
    if not os.path.exists(ANIMATION_DIR):
        return animations

    # Scan for folders
    for entry in os.listdir(ANIMATION_DIR):
        entry_path = os.path.join(ANIMATION_DIR, entry)
        if os.path.isdir(entry_path):
            # Find png files, sort them
            frames = glob.glob(os.path.join(entry_path, '*.png'))
            frames = [os.path.basename(f) for f in frames]
            frames.sort()
            if frames:
                # Use lowercase for animation name so ESP32 matches it properly
                animations[entry.lower()] = frames
                
    return animations

def get_local_ip():
    """Attempts to get the local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

@app.route('/')
def dashboard():
    """Simple web dashboard to view available animations."""
    animations = get_animations()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pixel Cat Server</title>
        <style>
            body { font-family: sans-serif; margin: 40px; background: #121212; color: #fff; }
            h1 { color: #00ffcc; }
            .anim-card { background: #1e1e1e; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid #00ffcc; }
            .details { color: #aaa; font-size: 0.9em; }
            .info-box { background: #333; padding: 10px; border-radius: 8px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>🐾 Pixel Cat Server 🐾</h1>
        <div class="info-box">
            <strong>Server IP:</strong> {{ ip }}<br>
            <strong>Port:</strong> 5000<br>
            <strong>Animation Directory:</strong> {{ anim_dir }}
        </div>
        <h2>Available Animations ({{ count }})</h2>
        {% for name, frames in animations.items() %}
        <div class="anim-card">
            <strong>{{ name }}</strong>
            <div class="details">{{ frames | length }} frames</div>
        </div>
        {% else %}
        <p>No animations found. Add some PNGs to the PixelCat folder!</p>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html, animations=animations, count=len(animations), ip=get_local_ip(), anim_dir=ANIMATION_DIR)

@app.route('/api/animations')
def api_animations():
    """Returns a list of all available animations and frame counts."""
    animations = get_animations()
    # Format for easy ESP32 consumption: [{"name": "idle", "frames": 3}, ...]
    result = []
    for name, frames in animations.items():
        result.append({
            "name": name,
            "frameCount": len(frames)
        })
    return jsonify(result)

@app.route('/api/animation/<name>')
def api_animation_frames(name):
    """Returns a list of frame filenames for a specific animation."""
    animations = get_animations()
    if name in animations:
        return jsonify({
            "name": name,
            "frames": animations[name]
        })
    return jsonify({"error": "Animation not found"}), 404

@app.route('/api/animation/<name>/<frame>')
def api_get_frame(name, frame):
    """Serves the actual PNG frame file."""
    # Prevent directory traversal
    safe_name = os.path.basename(name)
    safe_frame = os.path.basename(frame)
    
    file_path = os.path.join(ANIMATION_DIR, safe_name, safe_frame)
    if os.path.exists(file_path) and file_path.endswith('.png'):
        return send_file(file_path, mimetype='image/png')
    return jsonify({"error": "Frame not found"}), 404

if __name__ == '__main__':
    print(f"Starting Pixel Cat Server...")
    print(f"Local IP: {get_local_ip()}:5000")
    print(f"Monitoring folder: {ANIMATION_DIR}")
    # Run on all interfaces so ESP32 can connect
    app.run(host='0.0.0.0', port=5000, debug=True)
