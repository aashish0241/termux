import subprocess
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Store sent OTPs to prevent duplicates
sent_otps = set()

# Function to extract OTP (alphanumeric, 6 characters)
def extract_otp(message):
    otp = re.findall(r'OTP:\s*([A-Za-z0-9]{6})', message)
    if otp:
        print(f"Extracted OTP: {otp[0]}")
        return otp[0]
    else:
        print("No OTP found in the message.")
        return None

# Function to send OTP via Gmail SMTP
def send_otp_via_gmail(otp):
    try:
        sender_email = "timsinaaashish6@gmail.com"   # Corrected email format
        receiver_email = "aashishtimsinaaa@gmail.com"  # Corrected email format
        app_password = "ctwhmvnlycfuiehf"              # Use your app password (keep it secure)

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "OTP Notification"

        body = f"""
        <html>
            <body>
                <h2>OTP Alert</h2>
                <p>Your OTP is: <strong>{otp}</strong></p>
                <p>Please use this OTP to complete your verification process.</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        print(f"OTP {otp} sent to {receiver_email}.")
    except Exception as e:
        print(f"Error sending OTP email: {str(e)}")

# Function to get the latest SMS
def get_latest_sms():
    try:
        # Remove the '-u' flag as it is illegal and use only '-l'
        result = subprocess.run(['termux-sms-list', '-l', '1'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Failed to retrieve SMS (non-zero return code).")
            return None, None

        sms_list = json.loads(result.stdout)
        if not sms_list:
            print("No SMS messages found.")
            return None, None

        sms = sms_list[0]
        sender = sms.get('number', 'Unknown')
        message = sms.get('body', '')
        return sender, message

    except Exception as e:
        print(f"Error reading SMS: {e}")
        return None, None

# Function to monitor SMS continuously
def monitor_sms():
    while True:
        sender, message = get_latest_sms()
        if sender is None or message is None:
            # Skip extraction if SMS data is not read properly
            print("Skipping this iteration due to SMS read error.")
            time.sleep(5)
            continue

        print(f"SMS received from: {sender}")
        print(f"Message: {message}")

        # Process only messages from "AT_ALERT" (or change as needed)
        if sender == "AT_ALERT":
            print(f"Processing SMS from {sender}")
            otp = extract_otp(message)
            if otp:
                if otp not in sent_otps:
                    print(f"Sending OTP: {otp}")
                    send_otp_via_gmail(otp)
                    sent_otps.add(otp)
                else:
                    print(f"OTP {otp} has already been sent.")
            else:
                print("No valid OTP to process.")
        else:
            print("SMS sender not recognized for OTP processing.")

        # Delay between checks (adjust as needed)
        time.sleep(5)

if __name__ == "__main__":
    print("Starting SMS monitor...")
    monitor_sms()
