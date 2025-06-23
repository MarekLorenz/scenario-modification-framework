from PIL import Image, ImageSequence, ImageDraw, ImageFont
import os

# Create output directory if it doesn't exist
output_dir = "merged_images"
os.makedirs(output_dir, exist_ok=True)

# Load GIF
gif = Image.open("CHN_Qingdao-15_2_T-1.gif")

# Extract all frames
all_frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(gif)]

# Parameters for layout
frame_width, frame_height = all_frames[0].size
frames_per_image = 3
separator_width = 5  # Width of black separators

# Calculate total width including separators
total_width = frame_width * frames_per_image + separator_width * (frames_per_image - 1)

# Try to load a font, fall back to default if not available
try:
    font = ImageFont.truetype("Arial.ttf", 24)
except (OSError, IOError):
    font = ImageFont.load_default()

# Create multiple images with sliding window
total_frames = len(all_frames)
num_images = total_frames - frames_per_image + 1

for img_idx in range(num_images):
    # Create new image for this set of frames
    output_image = Image.new("RGBA", (total_width, frame_height), color=(255, 255, 255, 255))
    draw = ImageDraw.Draw(output_image)
    
    # Get frames for this image (sliding window)
    frames_for_this_image = all_frames[img_idx:img_idx + frames_per_image]
    
    # Paste frames side-by-side with separators
    current_x = 0
    for i, frame in enumerate(frames_for_this_image):
        # Paste the frame
        output_image.paste(frame, (current_x, 0))
        
        # Add frame number in top-left corner (actual frame index in GIF)
        frame_number = img_idx + i
        number_text = str(frame_number)
        # Create a white background for the number for better visibility
        text_bbox = draw.textbbox((0, 0), number_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Draw white background rectangle
        draw.rectangle([current_x + 5, 5, current_x + 5 + text_width + 10, 5 + text_height + 10], 
                       fill=(255, 255, 255, 200))
        
        # Draw the number in black
        draw.text((current_x + 10, 10), number_text, fill=(0, 0, 0, 255), font=font)
        
        # Move to next position
        current_x += frame_width
        
        # Add black separator (except after the last frame)
        if i < frames_per_image - 1:
            # Draw black separator line
            draw.rectangle([current_x, 0, current_x + separator_width, frame_height], 
                           fill=(0, 0, 0, 255))
            current_x += separator_width
    
    # Save image with descriptive filename in the merged_images folder
    start_frame = img_idx
    end_frame = img_idx + frames_per_image - 1
    filename = f"merged_frames_{start_frame}_to_{end_frame}.png"
    filepath = os.path.join(output_dir, filename)
    output_image.save(filepath)
    print(f"Saved {filepath} with frames {start_frame}-{end_frame}")

print(f"Created {num_images} images total from {total_frames} frames in '{output_dir}' folder")