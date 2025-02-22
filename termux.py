import subprocess
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Store sent OTPs to prevent sending them again
sent_otps = set()

# Function to extract OTP (6-digit number)
def extract_otp(message):
    otp = re.findall(r'\b[0-9]{6}\b', message)
    return otp[0] if otp else None

# Function to send OTP via Gmail using SMTP
def send_otp_via_gmail(otp):
    try:
        sender_email = "sumanoli2424@gmail.com"  # Replace with your Gmail address
        receiver_email = "sumanoli2424@gmail.com"  # Replace with the recipient email address
        app_password = "khem xytp xson lemh"  # Replace with your app password

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "OTP Alert"

        body = f"Your OTP is: {otp}\n\nAdditional Info: khem xytp xson lemh"
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Use TLS
            server.login(sender_email, app_password)  # Login using app password
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
        
        print(f"OTP {otp} sent to {receiver_email}.")
    except Exception as e:
        print(f"Failed to send OTP: {str(e)}")

# Function to monitor SMS and process
def monitor_sms():
    while True:
        # Get the latest SMS (1 message)
        result = subprocess.run(['termux-sms-list', '-l', '1'], capture_output=True, text=True)

        # If we successfully get the SMS, process it
        if result.returncode == 0:
            sms_data = result.stdout
            try:
                # Print the raw SMS data for debugging purposes
                print(f"Raw SMS data: {sms_data}")

                # Adjusted regular expressions to capture 'number' and 'body' from the raw data
                sender_match = re.search(r'"number": "(.*?)"', sms_data)  # This should capture the sender (e.g., "VFS")
                message_match = re.search(r'"body": "(.*?)"', sms_data)  # This should capture the OTP message body

                # Check if both sender and message were found
                if sender_match and message_match:
                    sender = sender_match.group(1)
                    message = message_match.group(1)

                    print(f"SMS received from: {sender}")
                    print(f"Message: {message}")

                    # Check if the sender is "VFS" or "AT_ALERT"
                    if sender == "VFS" or sender == "AT_ALERT":
                        print(f"Processing SMS from {sender}")

                        # Extract OTP from the message
                        otp = extract_otp(message)
                        
                        if otp:
                            if otp not in sent_otps:  # Send OTP only if it's not already sent
                                print(f"Extracted OTP: {otp}")
                                # Send the OTP via Gmail
                                send_otp_via_gmail(otp)
                                # Mark the OTP as sent
                                sent_otps.add(otp)
                            else:
                                print(f"OTP {otp} has already been sent.")
                        else:
                            print(f"No OTP found in message from {sender}")
                else:
                    print("Error: Could not find 'number' or 'body' in the SMS data.")

            except Exception as e:
                print(f"Error processing SMS: {e}")
        
        # Wait for 0.01 seconds before checking again
        time.sleep(0.01)

# Test Gmail Login to verify credentials
def test_gmail_login():
    sender_email = "sumanoli2424@gmail.com"
    app_password = "khem xytp xson lemh"  # Replace with the correct app password

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Use TLS
            server.login(sender_email, app_password)
            print("Login successful")
            server.quit()
    except Exception as e:
        print(f"Login failed: {e}")

if __name__ == "__main__":
    # Test Gmail login before running the monitoring function
    test_gmail_login()

    # If login is successful, start monitoring SMS
    monitor_sms()
