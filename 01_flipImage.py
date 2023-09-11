import cv2
import os

# Load the image
image_path = payload['ImageCapture']['image_path']
image = cv2.imread(image_path)

# Load data corner from payload
data_corner = payload['DeepD_D']['detects'][0]['objects']

# Create an empty list to store the corner coordinates
corner_sort = []

# Check if data_corner is empty
if len(data_corner) != 0:
    # Iterate over the corners and store the coordinates
    for i in range(len(data_corner)):
        x = data_corner[i]['x']  # Get the x coordinate of the corner
        y = data_corner[i]['y']  # Get the y coordinate of the corner
        corner_sort.append((x, y))
    
    # Find the min&max position x, y of corner
    min_x = min(corner_sort, key=lambda corner: corner[0])[0]
    max_y = min(corner_sort, key=lambda corner: corner[1])[1]

    # Calculate the height and width of the image
    height, width = image.shape[:2]

    output_path = r"C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/TempImage_flip.jpg"

    print("Min X: {}".format(min_x))
    print("Min Y: {}".format(max_y))
    print("58% H: {}".format(0.58 * height))
    print("50% w: {}".format(0.50 * width))
    print("--------------------------------------")

    if width < height and max_y > (0.58 * height):
        # Save the modified image
        print("rotate: 180")
        rotated_image = cv2.rotate(image, cv2.ROTATE_180)
        cv2.imwrite(output_path, rotated_image)
    elif width > height and min_x < (0.50 * width):
        # Save the modified image
        print("rotate: 90_CLOCKWISE")
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite(output_path, rotated_image)
    elif width > height and min_x > (0.50 * width):
        # Save the modified image
        print("rotate: 90_COUNTERCLOCKWISE")
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        cv2.imwrite(output_path, rotated_image)
    else:
        # Save the original image
        cv2.imwrite(output_path, image)

    # Read the saved image
    img = cv2.imread(output_path)

    # Update the payload with the rotated image path
    payload.clear()
    payload['modifi_img_path'] = output_path
else :
 payload['modifi_img_path'] = payload['ImageCapture']['image_path']