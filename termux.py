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
from dotenv import load_dotenv

# Load sensitive data from .env file
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

INTERVAL = 15  # seconds
TMP_FILE = "tmpLastTime.txt"

class bcolors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def send_email(subject, body):
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
    try:
        result = subprocess.run(["termux-sms-list", "-l", "5"], capture_output=True, text=True)
        sms_data = json.loads(result.stdout)
        return sms_data
    except Exception as e:
        print(f"{bcolors.FAIL}Error fetching SMS data: {e}{bcolors.ENDC}")
        return []

def extract_otp(message):
    # Regex to extract OTP: e.g., "OTP: 2N0PJ6"
    match = re.search(r"OTP:\s*([A-Za-z0-9]+)", message)
    return match.group(1) if match else None

def get_last_time():
    if not os.path.exists(TMP_FILE):
        now = datetime.datetime.now().isoformat()
        with open(TMP_FILE, "w") as f:
            f.write(now)
        return datetime.datetime.fromisoformat(now)
    with open(TMP_FILE, "r") as f:
        return datetime.datetime.fromisoformat(f.read().strip())

def update_last_time(timestamp):
    with open(TMP_FILE, "w") as f:
        f.write(timestamp)

def sms_forward():
    last_sms_time = get_last_time()
    print(f"Last SMS forwarded on {last_sms_time}")

    sms_list = fetch_sms()
    for sms in sms_list:
        try:
            received_time = datetime.datetime.fromisoformat(sms['received'])
        except Exception as e:
            print(f"{bcolors.FAIL}Error parsing date: {e}{bcolors.ENDC}")
            continue

        # Process only new messages
        if received_time > last_sms_time:
            otp = extract_otp(sms['body'])
            if otp:
                print(f"OTP found: {otp}")
                subject = "New OTP SMS"
                body = f"Sender: {sms['number']}\nMessage: {sms['body']}\nReceived: {sms['received']}\nExtracted OTP: {otp}"
                send_email(subject, body)
                update_last_time(sms['received'])

while True:
    sms_forward()
    time.sleep(INTERVAL)
