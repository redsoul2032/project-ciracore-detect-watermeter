# ---------------
# For rotating the image to make the image angle 
# ---------------

import shutil
import datetime
import os
import cv2
import numpy as np
import random
import math
from PIL import Image, ImageDraw

# Define a function to rotate the image
def rotate_image(image, angle_deg):
    height, width = image.shape[:2]
    
    if abs(angle_deg) > 60:
        angle_deg = max(min(angle_deg, 30), -30)
        
    rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle_deg, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
    return rotated_image

def resize_image(image, target_size):
    resized_image = cv2.resize(image, target_size)
    return resized_image

def enhance_image_quality(image):
    # Apply image color
    #gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #enhanced_image = cv2.equalizeHist(gray_image)

    # Apply image enhancement technique (e.g., sharpening)
    kernel_sharpening = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    enhance_image_quality = cv2.filter2D(image, -1, kernel_sharpening)
    return enhance_image_quality

# Load the image
image_path = payload['modifi_img_path']
image = cv2.imread(image_path)

# Load data corner from payload
data_corner = payload['DeepD_D']['detects'][0]['objects']

# Create an empty list to store the sorted corner coordinates
corner_sort = []

# Iterate over the corners and store the coordinates
for i in range(len(data_corner)):
    x = data_corner[i]['x']  # Get the x coordinate of the starting corner
    y = data_corner[i]['y']  # Get the y coordinate of the starting corner

    corner_sort.append((x, y))

# Sort the corner coordinates based on the y value in descending order
corner_sort.sort(key=lambda c:c[-1], reverse=True)

# Check if there is only one corner coordinate
if len(corner_sort) >= 2:
    # Initialize variables
    get_start = ()
    get_end = ()
    diff = 0
    height, width = image.shape[:2]

    # Show result in corner_sort[]
    for i, corner in enumerate(corner_sort):
        print("Corner {}: ({}, {})".format(i+1, corner[0], corner[1]))
    print("--------------------------------------")

    # Iterate over all possible pairs of coordinates
    if len(corner_sort) >= 2:
        for i in range(len(corner_sort)):
            for j in range(i, len(corner_sort)):
                if corner_sort[i] != corner_sort[j]:
                    if abs(corner_sort[i][0] - corner_sort[j][0]) > 30:
                        if abs(corner_sort[i][1] - corner_sort[j][1]) <= 40:
                            avg_y = abs((corner_sort[i][1]+corner_sort[j][1])/2)
                            print("Center of 2Y: {} + {} = {} / {}".format(corner_sort[i][1], corner_sort[j][1], avg_y, (0.5*height)))
                            if avg_y < (0.5*height):
                                if (avg_y > diff):
                                    get_start = corner_sort[i]
                                    get_end = corner_sort[j]
    print("--------------------------------------")


    # Check if a valid pair was found
    if get_start and get_end:
        x1, y1 = get_start
        x2, y2 = get_end
        print("start: ({}, {})".format(x1, y1))
        print("end: ({}, {})".format(x2, y2))
        print("--------------------------------------")

        # Calculate the angle of the line
        angle_rad = math.atan2(y2 - y1, x2 - x1)
        angle_deg = math.degrees(angle_rad)

        # Subtract 180 from angle_deg and set it to the new value if it exceeds 90 degrees
        if angle_deg > 90:
            angle_deg -= 180
        elif angle_deg < -90:
            angle_deg += 180
            
        # Draw a line on the image from corner 1 to corner 2
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 1)

        print("Angle of the line [{}, {}]: {} degrees".format(get_start, get_end, angle_deg))

        # Rotate the image if there are corner coordinates
        rotated_image = rotate_image(image, angle_deg)  # Specify the desired angle in degrees   

        # Resize the image to a target size
        target_size = (1440, 1920)
        resized_image = resize_image(rotated_image, target_size)

        # Enhance the quality of the image
        enhanced_image = enhance_image_quality(resized_image)

        # Save the modified image
        output_path = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/TempImage_rotate.jpg'
        cv2.imwrite(output_path, enhanced_image)

        # Read the saved image
        img = cv2.imread(output_path)

    else:
        # Resize the image to a target size
        target_size = (1440, 1920)
        resized_image = resize_image(image, target_size)

        # Enhance the quality of the image
        enhanced_image = enhance_image_quality(resized_image)

        # Save the modified image
        output_path = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/TempImage_rotate.jpg'
        cv2.imwrite(output_path, enhanced_image)

        # Read the saved image
        img = cv2.imread(output_path)

        print("No corner coordinates found.")

else:
    # Resize the image to a target size
    target_size = (1440, 1920)
    resized_image = resize_image(image, target_size)

    # Enhance the quality of the image
    enhanced_image = enhance_image_quality(resized_image)

    # Save the modified image
    output_path = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/TempImage_rotate.jpg'
    cv2.imwrite(output_path, enhanced_image)

    # Read the saved image
    img = cv2.imread(output_path)

    print("Error: Only one corner coordinate found.")
    
# Save the modified image
source_path = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/TempImage_original.jpg'
folder_path = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/original_image'
current_date = datetime.date.today().strftime("%d%m%Y")

# Find the latest run number within the folder
run_number = 1
while os.path.exists(os.path.join(folder_path, current_date + "_" + str(run_number) + ".jpg")):
    run_number += 1

# Generate the destination file path
destination_path = os.path.join(folder_path, current_date + "_" + str(run_number) + ".jpg")

# Copy the file from source to destination
shutil.copy2(source_path, destination_path)
    
# Update the payload with the rotated image path
payload.clear()
payload['file_run_number'] = current_date + "_" +  str(run_number)
payload['modifi_img_path'] = output_path