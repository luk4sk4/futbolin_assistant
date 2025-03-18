import cv2
import numpy as np

# Function to detect the purple object
def detect_purple_object(frame):
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the range for purple color in HSV
    lower_purple = np.array([130, 50, 50])  # Lower bound for purple
    upper_purple = np.array([160, 255, 255])  # Upper bound for purple

    # Create a mask for the purple color
    mask = cv2.inRange(hsv, lower_purple, upper_purple)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If contours are found, return the bounding box of the largest contour
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        if w > 10 and h > 10:
            return (x, y, w, h)
        else:
            return None
    else:
        return None

# Initialize the video capture
cap = cv2.VideoCapture(0)  # Use 0 for the default camera

while True:
    # Read a new frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture video")
        break

    # Detect the purple object in the frame
    bbox = detect_purple_object(frame)

    # If a purple object is detected, draw a bounding box around it
    if bbox:
        x, y, w, h = bbox
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green bounding box
        print("Purple object detected at:", x, y)

    # Display the frame
    cv2.imshow("Purple Object Detection", frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()