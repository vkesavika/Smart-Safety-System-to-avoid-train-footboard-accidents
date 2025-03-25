import serial
import time
import pyttsx3
import cv2
import smtplib
import os
from email.message import EmailMessage

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speech speed

# Email Configuration
EMAIL_SENDER = "kesavikav@gmail.com"
EMAIL_PASSWORD = "ukcy klri owfh tsxb"
EMAIL_RECEIVER = "meenachik22it@psnacet.edu.in"

# Open Serial Communication with Arduino
try:
    ser = serial.Serial("COM5", 9600, timeout=1)  # Adjust COM port accordingly
    time.sleep(2)  # Allow serial connection to stabilize
    print("Serial connection established!")
except serial.SerialException as e:
    print(f"Error: Could not open serial port: {e}")
    exit(1)

# Set FSR threshold for detection
FSR_THRESHOLD = 500  # Adjust based on testing

def play_audio_message():
    """Plays an audio warning message."""
    engine.say("Warning! Please move away from the footboard.")
    engine.runAndWait()

def capture_image():
    """Captures an image using the laptop camera."""
    cam = cv2.VideoCapture(0)
    time.sleep(2)  # Allow camera to adjust lighting

    ret, frame = cam.read()
    cam.release()

    if ret:
        image_path = "footboard_violation.jpg"
        cv2.imwrite(image_path, frame)
        print(f"Image captured: {image_path}")
        return image_path
    else:
        print("Failed to capture image.")
        return None

def send_email(image_path):
    """Sends an email with the captured image."""
    if image_path and os.path.exists(image_path):
        msg = EmailMessage()
        msg["Subject"] = "Footboard Violation Alert!"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg.set_content("A passenger is standing on the footboard. See attached image.")

        with open(image_path, "rb") as img:
            msg.add_attachment(img.read(), maintype="image", subtype="jpeg", filename="footboard_violation.jpg")

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
    else:
        print("No image available to send.")

# Main loop to check sensor data
while True:
    try:
        ser.reset_input_buffer()  # Clear old data
        time.sleep(0.5)  # Allow some time for new data

        if ser.in_waiting > 0:
            fsr_data = ser.readline().decode('utf-8').strip()
            print(f"FSR Status: {fsr_data}")

            # Extract FSR value from the received data
            try:
                fsr_value = int(fsr_data.split(":")[-1].strip())  # Extract numeric value
            except ValueError:
                print("Invalid FSR data received.")
                continue  # Skip processing invalid data

            # Check if the FSR value exceeds the threshold
            if fsr_value >= FSR_THRESHOLD:
                print("Person detected on footboard! Starting 30s countdown...")
                time.sleep(30)  # Wait 30 seconds

                ser.reset_input_buffer()  # Clear buffer before rechecking
                time.sleep(0.5)

                if ser.in_waiting > 0:
                    fsr_data = ser.readline().decode('utf-8').strip()
                    fsr_value = int(fsr_data.split(":")[-1].strip())
                    if fsr_value >= FSR_THRESHOLD:
                        print("Still on footboard! Playing warning audio...")
                        play_audio_message()
                        time.sleep(30)  # Wait another 30 seconds

                        ser.reset_input_buffer()
                        time.sleep(0.5)

                        if ser.in_waiting > 0:
                            fsr_data = ser.readline().decode('utf-8').strip()
                            fsr_value = int(fsr_data.split(":")[-1].strip())
                            if fsr_value >= FSR_THRESHOLD:
                                print("Person still on footboard! Capturing image...")
                                image_path = capture_image()
                                if image_path:
                                    print("Sending alert to TTE...")
                                    send_email(image_path)
            else:
                print("Footboard is clear.")

        time.sleep(1)  # Small delay to reduce CPU usage

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
        break  # Exit loop if serial connection is lost

    except KeyboardInterrupt:
        print("Program interrupted by user. Exiting...")
        break  # Exit loop on Ctrl+C
