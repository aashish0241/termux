import os
import json
import datetime
import time
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_USER = "timsinaaashish6@gmail.com"   # Store this in .env file
EMAIL_PASSWORD =  "ctwhmvnlycfuiehf" # Use App password for Gmail security
EMAIL_RECEIVER = "aashishtimsinaaa@gmail.com"

interV = 15  # Repeat interval in seconds
looper = False  # Control looping mechanism

tmpFile = "tmpLastTime.txt"
cfgFile = "config.txt"
mobile_number = "9861524169"

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def send_email(subject, body):
    """ Sends an email with given subject and body """
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

def smsforward(looping=False):
    global looper

    lastSMS = datetime.datetime.now()

    if not os.path.exists(tmpFile):
        print("Setting last forwarded time to current Date-Time")
        with open(tmpFile, "w") as tfile:
            tfile.write(str(lastSMS))
    else:
        with open(tmpFile, "r") as tfile:
            lastSMS = datetime.datetime.fromisoformat(tfile.read())

    print(f"Last SMS forwarded on {lastSMS}")

    try:
        jdata = os.popen("termux-sms-list -l 50").read()
        if not jdata:
            raise ValueError("No data returned from termux-sms-list")
        jd = json.loads(jdata)
    except Exception as e:
        print(f"{bcolors.FAIL}Error fetching SMS data: {e}{bcolors.ENDC}")
        return

    print(f"Reading {len(jd)} latest SMSs")

    for j in jd:
        if datetime.datetime.fromisoformat(j['received']) > lastSMS:
            if "otp" in j['body'].lower() and j['type'] == "inbox":
                print("OTP found")
                
                email_subject = "New Forwarded SMS"
                email_body = f"Sender: {j['number']}\nMessage: {j['body']}\nReceived: {j['received']}"
                
                send_email(email_subject, email_body)

                with open(tmpFile, "w") as tfile:
                    tfile.write(j['received'])

smsforward()

while True:
    time.sleep(interV)
    smsforward(looping=True)
