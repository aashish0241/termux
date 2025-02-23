import subprocess
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Store sent OTPs to prevent sending them again
sent_otps = set()

# Function to extract OTP (alphanumeric, 6 characters)
def extract_otp(message):
    otp = re.findall(r'OTP:\s*([A-Za-z0-9]{6})', message)
    return otp[0] if otp else None

# Function to send OTP via Gmail using SMTP with new credentials and HTML message type
def send_otp_via_gmail(otp):
    try:
        # New sender and receiver email addresses and app password
        sender_email = "timsinaaashish6@gmailcom"      # Replace with your new sender Gmail address
        receiver_email = "aashishtimsinaaa@gmailcom"  # Replace with your new receiver email address
        app_password = "ctwhmvnlycfuiehf"         # Replace with your new app password

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "OTP Notification"  # Changed subject

        # Create an HTML email body for a more styled message
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

        # Connect to Gmail SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Use TLS encryption
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print(f"OTP {otp} sent to {receiver_email}.")
    except Exception as e:
        print(f"Failed to send OTP: {str(e)}")

# Function to monitor SMS and process messages
def monitor_sms():
    while True:
        # Get the latest unread SMS (1 message)
        result = subprocess.run(['termux-sms-list', '-l', '1', '-u'], capture_output=True, text=True)

        # If SMS data is successfully retrieved, process it
        if result.returncode == 0:
            sms_data = result.stdout
            try:
                # Debug: print raw SMS data
                print(f"Raw SMS data: {sms_data}")

                # Extract sender and message body from the JSON output
                sender_match = re.search(r'"number": "(.*?)"', sms_data)
                message_match = re.search(r'"body": "(.*?)"', sms_data)

                if sender_match and message_match:
                    sender = sender_match.group(1)
                    message = message_match.group(1)

                    print(f"SMS received from: {sender}")
                    print(f"Message: {message}")

                    # Process only messages from "VFS" or "AT_ALERT"
                    if sender == "AT_ALERT":
                        print(f"Processing SMS from {sender}")
                        otp = extract_otp(message)
                        
                        if otp:
                            if otp not in sent_otps:  # Send OTP only if it hasn't been sent before
                                print(f"Extracted OTP: {otp}")
                                send_otp_via_gmail(otp)
                                sent_otps.add(otp)
                            else:
                                print(f"OTP {otp} has already been sent.")
                        else:
                            print(f"No OTP found in message from {sender}")
                else:
                    print("Error: Could not find 'number' or 'body' in the SMS data.")

            except Exception as e:
                print(f"Error processing SMS: {e}")
        
        # Wait briefly before checking again
        time.sleep(0.01)

if __name__ == "__main__":
    monitor_sms()
