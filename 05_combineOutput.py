import cv2
import os
import shutil
import datetime

# Load the images
image_number_path = "C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/Temp_detect_number.jpg"
image_dial_path = "C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/Temp_detect_dial.jpg"

image_number = cv2.imread(image_number_path)
image_dial = cv2.imread(image_dial_path)

# Check if the images are loaded successfully
if image_number is None or image_dial is None:
    print("Failed to load one or both images.")
    exit()

# Combine the images horizontally (side-by-side)
combined_image = cv2.hconcat([image_number, image_dial])

# Add a black bar at the bottom of the combined image
bar_height = 260
combined_image = cv2.copyMakeBorder(
    combined_image, 0, bar_height, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0)
)

# Add text on the black bar
result = payload['result']
text = "Result: "+ result
print(text)
text_position = (10, combined_image.shape[0] - 15)
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 8
text_color = (255, 255, 255)
text_thickness = 16
cv2.putText(combined_image,text,text_position, font,font_scale,text_color,text_thickness,cv2.LINE_AA,)

# Save the modified image
output_path = "C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/Combined_image.jpg"
folder_path = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/combined_image/{}.jpg'.format(payload['file_run_number'])
cv2.imwrite(output_path, combined_image)

# Copy the file from source to destination
shutil.copy2(output_path, folder_path)

# Check if the modified image is saved successfully
if os.path.exists(output_path):
    print("Images combined successfully. Combined image saved at:", output_path)
else:
    print("Failed to save the combined image.")

# Read the saved image
img = cv2.imread(output_path)
