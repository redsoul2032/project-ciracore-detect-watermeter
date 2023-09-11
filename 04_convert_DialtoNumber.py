import shutil
import datetime
import os
import math

# Function split angle degrees to number 0-9
def split_angle(angle_degrees):
    if angle_degrees < 0 or angle_degrees > 360:
        raise ValueError("Angle must be between 0 and 360 degrees")
    
    if   angle_degrees >= 72  and angle_degrees < 108: return 0
    elif angle_degrees >= 108 and angle_degrees < 144: return 1
    elif angle_degrees >= 144 and angle_degrees < 180: return 2
    elif angle_degrees >= 180 and angle_degrees < 216: return 3
    elif angle_degrees >= 216 and angle_degrees < 252: return 4
    elif angle_degrees >= 252 and angle_degrees < 288: return 5
    elif angle_degrees >= 288 and angle_degrees < 324: return 6
    elif angle_degrees >= 324 and angle_degrees > 0  : return 7
    elif angle_degrees >= 0   and angle_degrees < 36 : return 8
    elif angle_degrees >= 36  and angle_degrees < 72 : return 9

obj = payload['DeepD_D']['detects']
sorted_obj = sorted(obj, key=lambda x: x['y'])  # Sort data by 'y'
result = ""

for element in sorted_obj:
    if element["objects"]: 
        # Get data dial
        square_x = element["x"]
        square_y = element["y"]
        
        for obj_element in element["objects"]:
                # Get data pointer dial
                small_square_x = obj_element["x"]
                small_square_y = obj_element["y"]

                # Calculate the angle in radians
                angle = math.atan2(small_square_y - square_y, small_square_x - square_x)

                # Convert the angle to degrees
                angle_degrees = math.degrees(angle)
                if angle_degrees < 0:
                    angle_degrees += 360
                angle_degrees = (angle_degrees+180) %360

                # Print the result
                print("angle " + format(angle_degrees, '.2f') + "ํํ is " + str(split_angle(angle_degrees)))
                result += str(split_angle(angle_degrees))
    else:
        result += "_"
        
print("Result: "+str(result))

num = payload['number_digi']

# Save the modified image
source_path = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/Temp_detect_dial.jpg'
folder_path = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/detect_dial/{}.jpg'.format(payload['file_run_number'])

# Copy the file from source to destination
shutil.copy2(source_path, folder_path)

file_run_number = payload['file_run_number']

# Update the payload with the rotated image path
payload.clear()
payload['dial'] = result
payload['result'] = num  + "." + result
payload['file_run_number'] = file_run_number