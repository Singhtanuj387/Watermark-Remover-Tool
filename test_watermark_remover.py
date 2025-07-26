import os
import sys
import cv2
import numpy as np
from watermark_remover import WatermarkRemover

def create_test_video(output_path, width=640, height=480, duration=5, fps=30, with_watermark=True):
    """
    Create a test video with or without a watermark
    
    Parameters:
    - output_path: Path to save the test video
    - width: Video width
    - height: Video height
    - duration: Video duration in seconds
    - fps: Frames per second
    - with_watermark: Whether to add a watermark
    """
    # Create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Calculate total number of frames
    total_frames = duration * fps
    
    # Create a simple watermark (text)
    if with_watermark:
        watermark_text = "TEST WATERMARK"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2
        text_size = cv2.getTextSize(watermark_text, font, font_scale, font_thickness)[0]
        
        # Position the watermark in the bottom right corner
        text_x = width - text_size[0] - 10
        text_y = height - 10
    
    # Generate frames
    for i in range(total_frames):
        # Create a gradient background that changes over time
        t = i / total_frames  # Time variable (0 to 1)
        
        # Create a colored background with moving gradient
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                r = int(128 + 127 * np.sin(x * 0.01 + t * 6.28))
                g = int(128 + 127 * np.sin(y * 0.01 + t * 6.28))
                b = int(128 + 127 * np.sin((x+y) * 0.01 + t * 6.28))
                frame[y, x] = [b, g, r]
        
        # Add a moving circle
        circle_x = int(width/2 + width/3 * np.sin(t * 6.28))
        circle_y = int(height/2 + height/3 * np.cos(t * 6.28))
        cv2.circle(frame, (circle_x, circle_y), 30, (0, 0, 255), -1)
        
        # Add watermark if requested
        if with_watermark:
            cv2.putText(frame, watermark_text, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness)
        
        # Write the frame
        out.write(frame)
    
    # Release the VideoWriter
    out.release()
    
    print(f"Test video created: {output_path}")

def test_watermark_removal():
    """
    Test the watermark removal functionality
    """
    # Create test directory if it doesn't exist
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test video with watermark
    test_video_path = os.path.join(test_dir, 'test_video_with_watermark.mp4')
    create_test_video(test_video_path, with_watermark=True)
    
    # Create output path for processed video
    output_video_path = os.path.join(test_dir, 'test_video_without_watermark.mp4')
    
    # Create an instance of WatermarkRemover
    remover = WatermarkRemover()
    
    # Define watermark coordinates (bottom right corner)
    width, height = 640, 480
    text_width = 200  # Approximate width of the watermark text
    text_height = 30  # Approximate height of the watermark text
    x = width - text_width - 10
    y = height - text_height - 10
    watermark_coords = (x, y, text_width, text_height)
    
    # Define a progress callback function
    def progress_callback(progress, remaining_time):
        sys.stdout.write(f"\rProcessing: {progress}% complete")
        if remaining_time:
            sys.stdout.write(f" - Estimated time remaining: {remaining_time:.2f} seconds")
        sys.stdout.flush()
    
    print("Testing watermark removal...")
    
    # Test each method
    methods = ['inpaint', 'blend', 'frequency', 'exemplar']
    
    for method in methods:
        print(f"\n\nTesting method: {method}")
        method_output_path = os.path.join(test_dir, f'test_video_without_watermark_{method}.mp4')
        
        # Process the video
        success, message = remover.process_video(
            test_video_path,
            method_output_path,
            method=method,
            watermark_coords=watermark_coords,
            callback=progress_callback
        )
        
        print(f"\n{message} using {method} method")
    
    print("\n\nAll tests completed. Check the 'test' directory for the processed videos.")

if __name__ == "__main__":
    test_watermark_removal()