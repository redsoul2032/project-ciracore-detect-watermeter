import pickle
import os
import re
import time
import json
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request

def read_config(file_path):
    with open(file_path, "r") as config_file:
        config_data = json.load(config_file)
    return config_data


# Start timing the execution
start_time = time.time()

def Create_Service(client_secret_file, api_name, api_version, *scopes):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    cred = None

    # Set the pickle file path
    pickle_file = os.path.join(os.path.dirname(client_secret_file), 'token_{}_{}.pickle'.format(API_SERVICE_NAME, API_VERSION))

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt

# Read the value of temp_time from the file (read the last line)
try:
    with open(r"C:\CiRA-CORE\[detect_watermeter_cira]\logs\docs\logs_upload_time.txt", "r") as file:
        lines = file.readlines()
        temp_time = lines[-1].strip() if lines else None
except FileNotFoundError:
    temp_time = None

date_now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

CLIENT_SECRET_FILE = r'C:\CiRA-CORE\[detect_watermeter_cira]\src\api\client_secret.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

config_file_path = r'C:\CiRA-CORE\[detect_watermeter_cira]\src\api\config.json'
config_data = read_config(config_file_path)
if config_data and isinstance(config_data, list):
    first_config_entry = config_data[0]
    folder_id = first_config_entry.get("folder_id", "default_folder_id")
else:
    folder_id = "default_folder_id"


base_folder_path = r'C:\CiRA-CORE\[detect_watermeter_cira]\logs'

#upload_folder_names = ['docs', 'image/combined_image', 'image/detect_dial', 'image/detect_number', 'image/original_image']
upload_folder_names = ['docs', 'image/combined_image']

excluded_files = [
                  'logs_upload_time.txt', 
                  'TempImage_original.jpg', 
                  'Combined_image.jpg',
                  'Temp_detect_dial.jpg',
                  'Temp_detect_Number.jpg',
                  'TempImage_flip.jpg',
                  'TempImage_rotate.jpg',
                  'line',
                  'desktop.ini'
                  ]

# Update temp_time with the current time
temp_time = date_now + ", Upload: {}".format(", ".join(upload_folder_names))

# Save the updated temp_time to the file (append to a new line)
with open(r"C:\CiRA-CORE\[detect_watermeter_cira]\logs\docs\logs_upload_time.txt", "a") as file:
    file.write(temp_time + "\n")

print("---------------------------------")

def upload_files_recursive(folder_path, parent_folder_id):
    # Upload files from the current folder to the corresponding folder on Google Drive
    folder_name = os.path.basename(folder_path)
    folder_metadata = {
        'name': folder_name,
        'parents': [parent_folder_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }

    # Check if the folder already exists
    query = "name='{}' and '{}' in parents and mimeType='application/vnd.google-apps.folder'".format(folder_name, parent_folder_id)
    existing_folders = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    matching_folders = existing_folders.get('files', [])

    if not matching_folders:
        try:
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            print("Folder '{}' created with ID: {} \n".format(folder_name, folder['id']))
            folder_id = folder['id']  # Update folder_id with the newly created folder's ID
        except Exception as e:
            print("Error creating folder '{}': {} \n".format(folder_name, e.response['error']['message']))
            return
    else:
        folder_id = matching_folders[0]['id']
        print("\nFolder '{}' already exists in Google Drive.".format(folder_name))

    # Upload files from the current folder
    folder_files = os.listdir(folder_path)
    for file_name in folder_files:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isdir(file_path):
            # Recursively upload files from subfolders
            upload_files_recursive(file_path, folder_id)
        else:
            if file_name not in excluded_files:  # Check if file is not in the excluded files list
                file_metadata = {
                    'name': file_name,
                    'parents': [folder_id]
                }
                media = MediaFileUpload(file_path)

                # Check if the file already exists in the folder
                query = "name='{}' and '{}' in parents".format(file_name, folder_id)
                existing_files = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
                matching_files = existing_files.get('files', [])

                if matching_files:
                    file_id = matching_files[0]['id']
                    try:
                        # Retrieve the file's metadata to update only the parent(s) field
                        file_metadata = service.files().get(fileId=file_id, fields='parents').execute()
                        previous_parents = ",".join(file_metadata.get('parents', []))

                        # Remove the file from its current parent(s)
                        service.files().update(fileId=file_id, removeParents=previous_parents).execute()

                        # Add the file to the new parent folder
                        file = service.files().update(fileId=file_id, addParents=folder_id, fields='id').execute()
                        print(">> File '{}' updated on Google Drive".format(file_name))
                    except Exception as e:
                        print(">> Error uploading file '{}'".format(file_name))
                else:
                    try:
                        file_metadata = {
                            'name': file_name,
                            'parents': [folder_id]
                        }
                        media = MediaFileUpload(file_path)
                        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                        print(">> File '{}' uploaded to Google Drive".format(file_name))
                    except Exception as e:
                        print(">> Error uploading file '{}'".format(file_name))

# Check if folders exist in Google Drive, create if not
for folder_name in upload_folder_names:
    folder_path = os.path.join(base_folder_path, folder_name)
    upload_files_recursive(folder_path, folder_id)

print("\n---------------------------------")

payload.clear()
payload["upload_status"] = "Done"
