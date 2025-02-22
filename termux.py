import os
import json
import datetime
import time
import re
import smtplib
import ssl
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration: define credentials and parameters directly here.
EMAIL_USER = "timsinaaashish6@gmail.com"   # Gmail address used to send email
EMAIL_PASSWORD = "ctwhmvnlycfuiehf"          # App password for Gmail
EMAIL_RECEIVER = "aashishtimsinaaa@gmail.com" # Destination email address

INTERVAL = 15  # Repeat interval in seconds
TMP_FILE = "tmpLastTime.txt"

class bcolors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def send_email(subject, body):
    """Sends an email using Gmail's SMTP server."""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, EMAIL_RECEIVER, msg.as_string())

        print(f"{bcolors.OKGREEN}Email sent successfully to {EMAIL_RECEIVER}{bcolors.ENDC}")
    except Exception as e:
        print(f"{bcolors.FAIL}Error sending email: {e}{bcolors.ENDC}")

def fetch_sms():
    """Fetches the latest SMS messages using Termux:API."""
    try:
        # Fetch the last 5 SMS messages; adjust the limit as needed.
        result = subprocess.run(["termux-sms-list", "-l", "5"], capture_output=True, text=True)
        sms_data = json.loads(result.stdout)
        return sms_data
    except Exception as e:
        print(f"{bcolors.FAIL}Error fetching SMS data: {e}{bcolors.ENDC}")
        return []

def extract_otp(message):
    """Extracts the OTP from a message using regex. Returns None if not found."""
    match = re.search(r"OTP:\s*([A-Za-z0-9]+)", message)
    return match.group(1) if match else None

def get_last_time():
    """Reads the last processed SMS time from a file or creates it if missing."""
    if not os.path.exists(TMP_FILE):
        now = datetime.datetime.now().isoformat()
        with open(TMP_FILE, "w") as f:
            f.write(now)
        return datetime.datetime.fromisoformat(now)
    with open(TMP_FILE, "r") as f:
        return datetime.datetime.fromisoformat(f.read().strip())

def update_last_time(timestamp):
    """Updates the last processed SMS time in the file."""
    with open(TMP_FILE, "w") as f:
        f.write(timestamp)

def sms_forward():
    """Fetches SMS messages, checks for new OTP messages, and sends an email if found."""
    last_sms_time = get_last_time()
    print(f"Last SMS forwarded on {last_sms_time}")

    sms_list = fetch_sms()
    for sms in sms_list:
        try:
            received_time = datetime.datetime.fromisoformat(sms['received'])
        except Exception as e:
            print(f"{bcolors.FAIL}Error parsing date: {e}{bcolors.ENDC}")
            continue

        # Process only messages received after the last processed time
        if received_time > last_sms_time:
            otp = extract_otp(sms['body'])
            if otp:
                print(f"OTP found: {otp}")
                subject = "New OTP SMS"
                body = (
                    f"Sender: {sms['number']}\n"
                    f"Message: {sms['body']}\n"
                    f"Received: {sms['received']}\n"
                    f"Extracted OTP: {otp}"
                )
                send_email(subject, body)
                update_last_time(sms['received'])
            else:
                print("No OTP pattern found in this message.")

# Main loop to continuously check for new SMS messages.
while True:
    sms_forward()
    time.sleep(INTERVAL)
