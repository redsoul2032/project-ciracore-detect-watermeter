import datetime
from datetime import timedelta

try:
    with open(r"C:\CiRA-CORE\[detect_watermeter_cira]\logs\docs\logs_upload_time.txt", "r") as file:
        lines = file.readlines()
        temp_time = lines[-1].strip() if lines else None
except IOError:
    temp_time = None

date_now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

if temp_time is not None:
    temp_time_parts = temp_time.split(", ")

    temp_time_dt = datetime.datetime.strptime(temp_time_parts[0], "%d-%m-%Y %H:%M:%S")
    date_now_dt = datetime.datetime.strptime(date_now, "%d-%m-%Y %H:%M:%S")

    # Calculate the time difference
    time_diff = date_now_dt - temp_time_dt

    # Assuming you have defined `time_diff` somewhere before this point
    if time_diff > timedelta(hours=4):
        payload['upload'] = True
    else:
        payload['upload'] = False

else:
    # Update temp_time with the current time
    temp_time = date_now + ", [Reset, Set new time]"

    # Save the updated temp_time to the file (append to a new line)
    with open(r"C:\CiRA-CORE\[detect_watermeter_cira]\logs\docs\logs_upload_time.txt", "a") as file:
        file.write(temp_time + "\n")
