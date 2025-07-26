import os
import cv2
import numpy as np
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import uuid
import time
import uuid
import logging
import shutil
import subprocess
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, send_file, Response
from werkzeug.utils import secure_filename
import logging
import shutil
import subprocess
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, send_file, Response
from werkzeug.utils import secure_filename
from watermark_remover import WatermarkRemover

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
HLS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hls_segments')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'mkv'}

# Create necessary directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(HLS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['HLS_FOLDER'] = HLS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload size

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to check if a video file is valid and accessible
def check_video_file(file_path):
    """Check if a video file exists, is accessible, and is valid"""
    # Check if file exists
    if not os.path.isfile(file_path):
        return False, "File does not exist"
    
    # Check if file is accessible
    try:
        with open(file_path, 'rb') as f:
            # Just read a small portion to check access
            f.read(1024)
    except Exception as e:
        return False, f"File is not accessible: {str(e)}"
    
    # Check if file is a valid video
    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return False, "File is not a valid video (cannot be opened)"
        
        # Try to read the first frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return False, "File is not a valid video (cannot read frames)"
        
        return True, "Video file is valid"
    except Exception as e:
        return False, f"Error validating video: {str(e)}"

# Function to remove watermark from video (wrapper for WatermarkRemover class)
def remove_watermark(input_path, output_path, watermark_coords=None, method='inpaint'):
    """
    Remove watermark from video using specified method
    
    Parameters:
    - input_path: Path to input video
    - output_path: Path to save output video
    - watermark_coords: Tuple of (x, y, width, height) for watermark location
    - method: Method to use for watermark removal ('inpaint', 'blend', 'frequency', 'exemplar', or 'auto')
    """
    # Create an instance of WatermarkRemover
    remover = WatermarkRemover()
    
    # Map method names from the form to the actual method names in the WatermarkRemover class
    method_mapping = {
        'inpaint': 'inpaint',
        'blend': 'blend',
        'mask': 'inpaint',  # Map 'mask' to 'inpaint' for backward compatibility
        'frequency': 'frequency',
        'exemplar': 'exemplar',
        'auto': 'auto'
    }
    
    # Use the mapped method or default to 'inpaint'
    actual_method = method_mapping.get(method, 'inpaint')
    
    # Define a progress callback function
    def progress_callback(progress, remaining_time):
        print(f"Processing: {progress}% complete")
        if remaining_time:
            print(f"Estimated time remaining: {remaining_time:.2f} seconds")
    
    # Process the video
    success, message = remover.process_video(
        input_path,
        output_path,
        method=actual_method,
        watermark_coords=watermark_coords,
        callback=progress_callback
    )
    
    return success, message

# Routes
@app.route('/')
def index():
    return render_template('index.html', now=datetime.now())

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        flash('No video file part')
        return redirect(request.url)
    
    file = request.files['video']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        filename_base, file_extension = os.path.splitext(original_filename)
        unique_filename = f"{filename_base}_{uuid.uuid4().hex}{file_extension}"
        
        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Get watermark removal method and coordinates
        method = request.form.get('method', 'inpaint')
        
        # Check if custom coordinates are provided
        use_custom_coords = 'use_custom_coords' in request.form
        watermark_coords = None
        
        if use_custom_coords:
            try:
                x = int(request.form.get('x', 0))
                y = int(request.form.get('y', 0))
                width = int(request.form.get('width', 100))
                height = int(request.form.get('height', 50))
                watermark_coords = (x, y, width, height)
            except ValueError:
                flash('Invalid coordinate values. Using default coordinates.')
        
        # Check if auto-detection is requested
        use_auto_detect = 'use_auto_detect' in request.form
        if use_auto_detect:
            # Auto-detection will be handled by the WatermarkRemover class
            watermark_coords = None
        
        # Generate output filename
        output_filename = f"processed_{unique_filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Process the video (remove watermark)
        success, message = remove_watermark(file_path, output_path, watermark_coords, method)
        
        if success:
            return redirect(url_for('result', filename=output_filename))
        else:
            flash(message)
            return redirect(url_for('index'))
    
    flash('File type not allowed')
    return redirect(url_for('index'))

@app.route('/result/<filename>')
def result(filename):
    # Check if the file exists and is valid
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    is_valid, error_message = check_video_file(file_path)
    
    if not is_valid:
        app.logger.error(f"Video file issue: {error_message}")
        flash(f"Video file issue: {error_message}")
        return redirect(url_for('index'))
        
    return render_template('result.html', filename=filename, now=datetime.now())

@app.route('/download/<filename>')
def download(filename):
    # Check if the file exists
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    is_valid, error_message = check_video_file(file_path)
    
    if not is_valid:
        app.logger.error(f"Video file issue: {error_message}")
        flash(f"Video file issue: {error_message}")
        return redirect(url_for('index'))
        
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

@app.route('/video/<filename>')
def video(filename):
    # Check if the file exists and is valid
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    if not os.path.isfile(file_path):
        app.logger.error(f"File not found: {file_path}")
        return "File not found", 404
    
    # Get file size for logging
    file_size = os.path.getsize(file_path)
    app.logger.info(f"Serving video file: {file_path}, Size: {file_size} bytes")
        
    # Get the file extension to determine the correct MIME type
    file_extension = os.path.splitext(filename)[1].lower()
    mime_types = {
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.wmv': 'video/x-ms-wmv',
        '.mkv': 'video/x-matroska'
    }
    # Default to mp4 if extension not recognized
    mimetype = mime_types.get(file_extension, 'video/mp4')
    app.logger.info(f"Using MIME type: {mimetype} for file extension: {file_extension}")
    
    try:
        # Log request headers for debugging
        app.logger.info(f"Request headers: {request.headers}")
        
        # Generate ETag based on file modification time and size
        file_mtime = os.path.getmtime(file_path)
        etag = f"\"{file_mtime}-{file_size}\"" 
        
        # Check if client sent If-None-Match header
        if request.headers.get('If-None-Match') == etag:
            return '', 304  # Not Modified
        
        # Use send_from_directory instead of send_file
        response = send_from_directory(
            app.config['OUTPUT_FOLDER'],
            filename,
            mimetype=mimetype,
            as_attachment=False
        )
        
        # Add headers to prevent caching issues
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        # Add Accept-Ranges header to support seeking
        response.headers['Accept-Ranges'] = 'bytes'
        # Add ETag for conditional requests
        response.headers['ETag'] = etag
        
        # Log response headers for debugging
        app.logger.info(f"Response headers: {response.headers}")
        
        return response
    except Exception as e:
        app.logger.error(f"Error serving video file: {e}")
        return f"Error: {str(e)}", 500

@app.route('/test_video')
def test_video():
    return render_template('test_video.html')

@app.route('/direct_test')
def direct_test():
    return render_template('direct_test.html')

@app.route('/simple_test')
def simple_test():
    return render_template('simple_test.html')

@app.route('/direct_video/<filename>')
def direct_video(filename):
    """A simpler route for serving video files directly"""
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    if not os.path.isfile(file_path):
        app.logger.error(f"File not found: {file_path}")
        return "File not found", 404
    
    # Get the file extension to determine the correct MIME type
    file_extension = os.path.splitext(filename)[1].lower()
    mime_types = {
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.wmv': 'video/x-ms-wmv',
        '.mkv': 'video/x-matroska'
    }
    # Default to mp4 if extension not recognized
    mimetype = mime_types.get(file_extension, 'video/mp4')
    
    try:
        # Use a very simple approach with send_file
        return send_file(file_path, mimetype=mimetype)
    except Exception as e:
        app.logger.error(f"Error serving video file: {e}")
        return f"Error: {str(e)}", 500

@app.route('/hls/<filename>/master.m3u8')
def hls_master(filename):
    """Serve the HLS master playlist"""
    # Check if the original file exists
    # First, try to find the file as-is (in case filename already has extension)
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    # If not found, try adding .mp4 extension (most common case)
    if not os.path.isfile(file_path):
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{filename}.mp4")
    
    # If still not found, try with processed_ prefix
    if not os.path.isfile(file_path):
        processed_filename = f"processed_{filename}"
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], processed_filename)
        
        # Try with processed_ prefix and .mp4 extension
        if not os.path.isfile(file_path):
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{processed_filename}.mp4")
            
            # If still not found, log error and return 404
            if not os.path.isfile(file_path):
                app.logger.error(f"Original file not found for HLS: {filename}")
                return "File not found", 404
    
    # Extract base filename without extension for HLS directory
    filename_base = os.path.splitext(os.path.basename(file_path))[0]
    app.logger.info(f"HLS request for {filename}, using file: {file_path}, base: {filename_base}")
    
    # Create HLS directory for this video if it doesn't exist
    video_hls_dir = os.path.join(app.config['HLS_FOLDER'], filename_base)
    os.makedirs(video_hls_dir, exist_ok=True)
    
    # Check if master playlist already exists
    master_playlist_path = os.path.join(video_hls_dir, 'master.m3u8')
    
    if not os.path.isfile(master_playlist_path):
        # Generate HLS segments and playlists using FFmpeg
        try:
            app.logger.info(f"Generating HLS segments for {filename_base}")
            
            # Define quality levels (resolution, bitrate)
            qualities = [
                {'name': '720p', 'resolution': '1280x720', 'bitrate': '2000k'},
                {'name': '480p', 'resolution': '854x480', 'bitrate': '1000k'},
                {'name': '360p', 'resolution': '640x360', 'bitrate': '500k'}
            ]
            
            # Create master playlist content
            master_content = "#EXTM3U\n#EXT-X-VERSION:3\n"
            
            for quality in qualities:
                # Add each quality variant to the master playlist
                master_content += f"#EXT-X-STREAM-INF:BANDWIDTH={quality['bitrate'].replace('k', '000')},RESOLUTION={quality['resolution']}\n"
                master_content += f"{quality['name']}.m3u8\n"
                
                # Generate HLS segments for this quality
                variant_output = os.path.join(video_hls_dir, f"{quality['name']}.m3u8")
                segment_pattern = os.path.join(video_hls_dir, f"{quality['name']}_%03d.ts")
                
                ffmpeg_cmd = [
                    'ffmpeg', '-y', '-i', file_path,
                    '-c:v', 'libx264', '-c:a', 'aac',
                    '-b:v', quality['bitrate'], '-b:a', '128k',
                    '-vf', f"scale={quality['resolution'].split('x')[0]}:{quality['resolution'].split('x')[1]}",
                    '-preset', 'fast', '-g', '48', '-sc_threshold', '0',
                    '-hls_time', '10', '-hls_playlist_type', 'vod',
                    '-hls_segment_filename', segment_pattern,
                    variant_output
                ]
                
                app.logger.info(f"Running FFmpeg command: {' '.join(ffmpeg_cmd)}")
                subprocess.run(ffmpeg_cmd, check=True)
                app.logger.info(f"Generated HLS variant: {quality['name']}")
            
            # Write master playlist
            with open(master_playlist_path, 'w') as f:
                f.write(master_content)
                
            app.logger.info(f"HLS conversion complete for {filename_base}")
            
        except Exception as e:
            app.logger.error(f"Error generating HLS content: {e}")
            return f"Error generating HLS content: {str(e)}", 500
    
    # Serve the master playlist
    return send_from_directory(video_hls_dir, 'master.m3u8', mimetype='application/vnd.apple.mpegurl')

@app.route('/hls/<filename>/<segment>')
def hls_segment(filename, segment):
    """Serve an HLS segment or variant playlist"""
    # Extract base filename without extension for HLS directory
    filename_base = os.path.splitext(filename)[0]
    video_hls_dir = os.path.join(app.config['HLS_FOLDER'], filename_base)
    
    if not os.path.exists(video_hls_dir):
        # Try with processed_ prefix if not found
        processed_filename_base = f"processed_{filename_base}"
        video_hls_dir = os.path.join(app.config['HLS_FOLDER'], processed_filename_base)
        if not os.path.exists(video_hls_dir):
            app.logger.error(f"HLS directory not found: {video_hls_dir}")
            return "HLS directory not found", 404
    
    if segment.endswith('.m3u8'):
        mimetype = 'application/vnd.apple.mpegurl'
    elif segment.endswith('.ts'):
        mimetype = 'video/mp2t'
    else:
        mimetype = 'application/octet-stream'
    
    return send_from_directory(video_hls_dir, segment, mimetype=mimetype)

# Clean up old files periodically (files older than 24 hours)
@app.before_request
def cleanup_old_files():
    # Run cleanup once per hour (approximately)
    if int(time.time()) % 3600 < 10:  # Run in the first 10 seconds of each hour
        cleanup_time = 24 * 3600  # 24 hours in seconds
        current_time = time.time()
        
        # Clean uploads folder
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path) and (current_time - os.path.getmtime(file_path)) > cleanup_time:
                os.remove(file_path)
        
        # Clean outputs folder
        for filename in os.listdir(OUTPUT_FOLDER):
            file_path = os.path.join(OUTPUT_FOLDER, filename)
            if os.path.isfile(file_path) and (current_time - os.path.getmtime(file_path)) > cleanup_time:
                os.remove(file_path)
                
        # Clean HLS segments folder
        for dirname in os.listdir(HLS_FOLDER):
            dir_path = os.path.join(HLS_FOLDER, dirname)
            if os.path.isdir(dir_path) and (current_time - os.path.getmtime(dir_path)) > cleanup_time:
                shutil.rmtree(dir_path)

if __name__ == '__main__':
    app.run(debug=True)
