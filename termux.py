import subprocess
import re
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Store processed OTPs to prevent duplicate email sending
processed_otps = set()

def extract_otp(message):
    """
    Extracts a 6-character alphanumeric OTP from the message.
    Expected format: 'OTP: <OTP_CODE>'
    """
    otp_matches = re.findall(r'OTP:\s*([A-Za-z0-9]{6})', message)
    if otp_matches:
        print(f"[DEBUG] Extracted OTP: {otp_matches[0]}")
        return otp_matches[0]
    else:
        print("[DEBUG] No OTP found in the message.")
        return None

def send_otp_via_gmail(otp):
    """
    Sends the OTP via Gmail using SMTP with an HTML-formatted email.
    Update sender_email, receiver_email, and app_password with your credentials.
    """
    try:
        sender_email = "timsinaaashish6@gmail.com"   # Correct sender email address
        receiver_email = "aashishtimsinaaa@gmail.com"  # Correct receiver email address
        app_password = "ctwhmvnlycfuiehf"              # Replace with your Gmail App Password

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "OTP Notification"

        html_body = f"""
        <html>
            <body>
                <h2>OTP Alert</h2>
                <p>Your OTP is: <strong>{otp}</strong></p>
                <p>Please use this OTP to complete your verification process.</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Enable TLS encryption
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        print(f"[INFO] OTP {otp} sent to {receiver_email}.")
    except Exception as e:
        print(f"[ERROR] Failed to send OTP: {e}")

def monitor_sms():
    """
    Retrieves unread SMS messages using termux-sms-list (-u flag).
    Processes messages from sender 'AT_ALERT' by extracting the OTP and sending an email.
    """
    while True:
        # Retrieve unread SMS messages using the -u flag
        result = subprocess.run(['termux-sms-list', '-u'], capture_output=True, text=True)
        if result.returncode != 0:
            print("[ERROR] Failed to retrieve SMS data.")
            time.sleep(2)
            continue

        sms_data = result.stdout
        try:
            sms_list = json.loads(sms_data)
            if not isinstance(sms_list, list):
                print("[ERROR] Unexpected SMS data format.")
                time.sleep(2)
                continue

            for sms in sms_list:
                # Confirm SMS is unread; 0 indicates unread
                if sms.get("read", 1) != 0:
                    continue

                sender = sms.get("number", "")
                message = sms.get("body", "")
                print(f"[DEBUG] Unread SMS from: {sender}")
                print(f"[DEBUG] Message: {message}")

                # Process only messages from the specific sender "AT_ALERT"
                if sender == "AT_ALERT":
                    otp = extract_otp(message)
                    if otp:
                        if otp not in processed_otps:
                            send_otp_via_gmail(otp)
                            processed_otps.add(otp)
                        else:
                            print(f"[INFO] OTP {otp} has already been processed.")
                    else:
                        print("[DEBUG] No OTP found in this SMS.")

        except json.JSONDecodeError as je:
            print(f"[ERROR] JSON decoding error: {je}")
        except Exception as e:
            print(f"[ERROR] Exception during SMS processing: {e}")

        # Pause before checking for new messages
        time.sleep(2)

if __name__ == "__main__":
    monitor_sms()
