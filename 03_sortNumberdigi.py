import shutil
import datetime
import os

# Load data from payload
objects = payload['DeepD_D']['detects'][0]['objects']

if(len(objects) > 0) :
    for i in range(len(objects)):
        for j in range(len(objects) - 1):
            if objects[j]['x'] > objects[j+1]['x']:
                # Swap
                tmp = objects[j]
                objects[j] = objects[j+1]
                objects[j+1] = tmp

    number_digi = ""
    number_confi = 0

    for i in range(len(objects)):
        number_digi += objects[i]['name']
        number_confi += objects[i]['confidence']
        
    number_confi = number_confi / len(objects)

    print(number_digi)
    print(number_confi)

    # Save the modified image
    source_path = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/Temp_detect_Number.jpg'
    folder_path = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/detect_number/{}.jpg'.format(payload['file_run_number'])

    # Copy the file from source to destination
    shutil.copy2(source_path, folder_path)

    # Read the saved image
    img = cv2.imread('C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/TempImage_rotate.jpg')
    
    file_run_number = payload['file_run_number']
    
    # Update the payload with the rotated image path
    payload.clear()
    payload['number_digi'] = number_digi
    payload['number_confi'] = number_confi
    payload['file_run_number'] = file_run_number
    payload['modifi_img_path'] = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/TempImage_rotate.jpg'
    
else:
    # Save the modified image
    source_path = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/Temp_detect_Number.jpg'
    folder_path = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/detect_number/{}.jpg'.format(payload['file_run_number'])

    # Copy the file from source to destination
    shutil.copy2(source_path, folder_path)

    # Read the saved image
    img = cv2.imread('C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/TempImage_rotate.jpg')
    
    file_run_number = payload['file_run_number']

    # Update the payload with the rotated image path
    payload['number_digi'] = "NF"
    payload['number_confi'] = "NF"
    payload['file_run_number'] = file_run_number
    payload['modifi_img_path'] = 'C:/CiRA-CORE/[detect_watermeter_cira]/logs/image/TempImage_rotate.jpg'
