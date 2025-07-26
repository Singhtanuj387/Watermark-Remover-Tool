import cv2
import numpy as np
from scipy import ndimage
import os
import time

class WatermarkRemover:
    """
    A class for removing watermarks from videos using various techniques.
    """
    
    def __init__(self):
        """Initialize the WatermarkRemover class"""
        pass
    
    def detect_watermark(self, frames, num_frames=10):
        """
        Attempt to automatically detect the watermark location by analyzing multiple frames
        
        Parameters:
        - frames: List of video frames
        - num_frames: Number of frames to analyze
        
        Returns:
        - (x, y, width, height): Coordinates of detected watermark or None if not detected
        """
        if len(frames) < num_frames:
            num_frames = len(frames)
        
        # Sample frames at regular intervals
        step = len(frames) // num_frames
        sample_frames = [frames[i * step] for i in range(num_frames)]
        
        # Convert frames to grayscale
        gray_frames = [cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) for frame in sample_frames]
        
        # Calculate the standard deviation of each pixel across frames
        stacked = np.stack(gray_frames)
        std_dev = np.std(stacked, axis=0)
        
        # Threshold the standard deviation to find static areas
        _, thresh = cv2.threshold(std_dev.astype(np.uint8), 5, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Find the largest contour (likely to be the watermark)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Validate the detected region (basic checks)
        frame_height, frame_width = gray_frames[0].shape
        min_size = min(frame_width, frame_height) * 0.01  # Minimum 1% of frame dimension
        max_size = min(frame_width, frame_height) * 0.3   # Maximum 30% of frame dimension
        
        if w < min_size or h < min_size or w > max_size or h > max_size:
            return None
        
        return (x, y, w, h)
    
    def remove_watermark_inpaint(self, frame, mask):
        """
        Remove watermark using inpainting technique
        
        Parameters:
        - frame: Input video frame
        - mask: Binary mask where watermark is located (255 for watermark, 0 elsewhere)
        
        Returns:
        - Processed frame with watermark removed
        """
        # Apply inpainting
        result = cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)
        return result
    
    def remove_watermark_blend(self, frame, mask, kernel_size=25):
        """
        Remove watermark by blending with surrounding pixels
        
        Parameters:
        - frame: Input video frame
        - mask: Binary mask where watermark is located (255 for watermark, 0 elsewhere)
        - kernel_size: Size of the Gaussian blur kernel
        
        Returns:
        - Processed frame with watermark removed
        """
        # Create a blurred version of the frame
        blur = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        
        # Create a normalized mask (0-1 range)
        norm_mask = mask.astype(float) / 255.0
        norm_mask = np.expand_dims(norm_mask, axis=2)  # Add channel dimension
        norm_mask = np.repeat(norm_mask, 3, axis=2)    # Repeat for each color channel
        
        # Blend the original frame and the blurred frame using the mask
        result = (1 - norm_mask) * frame + norm_mask * blur
        return result.astype(np.uint8)
    
    def remove_watermark_frequency(self, frame, mask):
        """
        Remove watermark using frequency domain filtering
        
        Parameters:
        - frame: Input video frame
        - mask: Binary mask where watermark is located (255 for watermark, 0 elsewhere)
        
        Returns:
        - Processed frame with watermark removed
        """
        # Process each channel separately
        result = np.zeros_like(frame)
        
        for c in range(3):  # For each color channel
            # Get the current channel
            channel = frame[:, :, c]
            
            # Apply FFT
            f_transform = np.fft.fft2(channel)
            f_shift = np.fft.fftshift(f_transform)
            
            # Create a high-pass filter (to remove the watermark frequencies)
            rows, cols = channel.shape
            crow, ccol = rows // 2, cols // 2
            
            # Create a mask for the filter (1 for frequencies to keep, 0 for frequencies to remove)
            mask_fft = np.ones((rows, cols), np.uint8)
            r = 30  # Filter radius
            center = [crow, ccol]
            x, y = np.ogrid[:rows, :cols]
            mask_area = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= r*r
            mask_fft[mask_area] = 0
            
            # Apply the filter
            f_shift_filtered = f_shift * mask_fft
            
            # Inverse FFT
            f_ishift = np.fft.ifftshift(f_shift_filtered)
            img_back = np.fft.ifft2(f_ishift)
            img_back = np.abs(img_back)
            
            # Normalize to 0-255 range
            img_back = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX)
            
            # Store the processed channel
            result[:, :, c] = img_back
        
        return result.astype(np.uint8)
    
    def remove_watermark_exemplar(self, frame, mask, patch_size=9):
        """
        Remove watermark using exemplar-based inpainting (similar to Photoshop's content-aware fill)
        
        Parameters:
        - frame: Input video frame
        - mask: Binary mask where watermark is located (255 for watermark, 0 elsewhere)
        - patch_size: Size of patches for exemplar-based inpainting
        
        Returns:
        - Processed frame with watermark removed
        """
        # This is a simplified version of exemplar-based inpainting
        # For a full implementation, more complex algorithms like PatchMatch would be needed
        
        # Convert mask to binary (0 for watermark, 1 for non-watermark)
        mask_inv = cv2.bitwise_not(mask)
        mask_inv = mask_inv.astype(np.uint8) // 255
        
        # Process each channel separately
        result = np.zeros_like(frame)
        
        for c in range(3):  # For each color channel
            # Get the current channel
            channel = frame[:, :, c]
            
            # Apply exemplar-based inpainting (simplified version)
            # Here we use a median filter as a simple approximation
            filled = ndimage.median_filter(channel, size=patch_size)
            
            # Combine the original and filled regions using the mask
            result[:, :, c] = channel * mask_inv + filled * (1 - mask_inv)
        
        return result.astype(np.uint8)
    
    def process_video(self, input_path, output_path, method='inpaint', watermark_coords=None, callback=None):
        """
        Process a video to remove watermark
        
        Parameters:
        - input_path: Path to input video file
        - output_path: Path to save output video file
        - method: Watermark removal method ('inpaint', 'blend', 'frequency', 'exemplar', or 'auto')
        - watermark_coords: Tuple of (x, y, width, height) for watermark location
        - callback: Optional callback function to report progress
        
        Returns:
        - (success, message): Tuple indicating success status and message
        """
        # Open the video file
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return False, "Error: Could not open video file"
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # If method is 'auto', we'll try to detect the best method based on the video
        if method == 'auto':
            # Default to inpaint for now
            method = 'inpaint'
        
        # If watermark coordinates are not provided, try to detect them
        if watermark_coords is None:
            # Read a sample of frames for watermark detection
            sample_frames = []
            max_samples = min(30, frame_count)  # Use at most 30 frames for detection
            step = max(1, frame_count // max_samples)
            
            for i in range(0, frame_count, step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    sample_frames.append(frame)
                if len(sample_frames) >= max_samples:
                    break
            
            # Try to detect the watermark
            watermark_coords = self.detect_watermark(sample_frames)
            
            # Reset the video capture to the beginning
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # If watermark detection failed, use default coordinates
            if watermark_coords is None:
                # Default to bottom right corner, 20% of width and 10% of height
                w_width = int(width * 0.2)
                w_height = int(height * 0.1)
                x = width - w_width
                y = height - w_height
                watermark_coords = (x, y, w_width, w_height)
        
        # Extract watermark coordinates
        x, y, w, h = watermark_coords
        
        # Create a mask for the watermark region
        mask = np.zeros((height, width), dtype=np.uint8)
        mask[y:y+h, x:x+w] = 255
        
        # Process each frame
        frame_number = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Apply the selected watermark removal method
            if method == 'inpaint':
                processed_frame = self.remove_watermark_inpaint(frame, mask)
            elif method == 'blend':
                processed_frame = self.remove_watermark_blend(frame, mask)
            elif method == 'frequency':
                processed_frame = self.remove_watermark_frequency(frame, mask)
            elif method == 'exemplar':
                processed_frame = self.remove_watermark_exemplar(frame, mask)
            else:
                # Default to inpaint
                processed_frame = self.remove_watermark_inpaint(frame, mask)
            
            # Write the processed frame to output video
            out.write(processed_frame)
            
            # Update progress
            frame_number += 1
            if callback and frame_number % max(1, int(frame_count / 100)) == 0:
                progress = int((frame_number / frame_count) * 100)
                elapsed_time = time.time() - start_time
                remaining_frames = frame_count - frame_number
                
                # Estimate remaining time
                if frame_number > 0 and elapsed_time > 0:
                    frames_per_second = frame_number / elapsed_time
                    estimated_remaining_time = remaining_frames / frames_per_second
                    callback(progress, estimated_remaining_time)
                else:
                    callback(progress, None)
        
        # Release resources
        cap.release()
        out.release()
        
        return True, "Watermark removal completed successfully"


# Example usage
if __name__ == "__main__":
    # Create an instance of WatermarkRemover
    remover = WatermarkRemover()
    
    # Define input and output paths
    input_video = "input.mp4"
    output_video = "output.mp4"
    
    # Define watermark coordinates (x, y, width, height)
    # If None, the remover will try to detect the watermark automatically
    watermark_coords = None
    
    # Define a callback function to report progress
    def progress_callback(progress, remaining_time):
        if remaining_time:
            print(f"Progress: {progress}% - Estimated time remaining: {remaining_time:.2f} seconds")
        else:
            print(f"Progress: {progress}%")
    
    # Process the video
    success, message = remover.process_video(
        input_video,
        output_video,
        method='inpaint',  # Options: 'inpaint', 'blend', 'frequency', 'exemplar', 'auto'
        watermark_coords=watermark_coords,
        callback=progress_callback
    )
    
    print(message)