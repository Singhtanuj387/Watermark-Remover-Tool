# Video Watermark Remover

A web application that helps users remove watermarks from videos using computer vision techniques.

## Features

- Upload videos in various formats (MP4, AVI, MOV, WMV, MKV)
- Three different watermark removal methods:
  - Inpaint: Best for logos and text watermarks
  - Blend: Best for semi-transparent watermarks
  - Mask: Best for static watermarks with high contrast
- Custom watermark location specification
- Preview processed videos before downloading
- Automatic cleanup of files after 24 hours

## Technologies Used

- Python 3.8+
- Flask (Web Framework)
- OpenCV (Computer Vision)
- NumPy (Numerical Processing)
- FFmpeg (Video Processing)
- Bootstrap 5 (Frontend)

## Installation

### Quick Start

1. For Windows users, simply run the `run.bat` file
2. For macOS/Linux users, run the `run.sh` file

These scripts will set up the environment, install dependencies, and start the application automatically.

### Manual Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/video-watermark-remover.git
   cd video-watermark-remover
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Make sure FFmpeg is installed on your system:
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - macOS: `brew install ffmpeg`
   - Linux: `apt-get install ffmpeg`

### Troubleshooting Dependencies

If you encounter issues with dependency installation:

1. Run the dependency test script to identify problems:
   ```
   python test_dependencies.py
   ```

2. Refer to the detailed troubleshooting guide in `docs/dependency_troubleshooting.md`

3. Common issues include:
   - NumPy and OpenCV compatibility problems
   - Missing system libraries or compilers
   - Python version compatibility

## Usage

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. Upload a video file and select the appropriate watermark removal method

4. Optionally specify the exact location of the watermark for better results

5. Click "Remove Watermark" and wait for processing to complete

6. Preview and download your watermark-free video

## Watermark Removal Methods

### Inpaint
Uses OpenCV's inpainting algorithm to reconstruct the watermarked area based on surrounding pixels. Works best for logos and text watermarks with clear boundaries.

### Blend
Applies Gaussian blur to the watermarked area, effectively blending it with surrounding pixels. Works best for semi-transparent watermarks.

### Mask
Creates a binary mask of the watermark and applies it to remove the watermark. Works best for static watermarks with high contrast against the background.

## Limitations

- The application works best with static watermarks (watermarks that stay in the same position throughout the video)
- Very complex or animated watermarks may not be completely removed
- Processing large videos may take significant time
- Maximum upload size is limited to 500MB

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [OpenCV](https://opencv.org/) for computer vision algorithms
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for the frontend design