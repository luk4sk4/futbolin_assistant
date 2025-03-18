import cv2
import numpy as np

roi_coordinates = []
drawing = False
frame = None  # Initialize frame variable

def select_roi(event, x, y, flags, param):
    global roi_coordinates, drawing, frame

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        roi_coordinates = [(x, y)]  # Start point

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        roi_coordinates.append((x, y))  # End point
        cv2.rectangle(frame, roi_coordinates[0], roi_coordinates[1], (0, 255, 0), 2)
        cv2.imshow("Frame", frame)
        
        
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

cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", select_roi)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Display the frame
    cv2.imshow("Frame", frame)

    # If ROI is selected, extract and display it
    if len(roi_coordinates) == 2:
        x1, y1 = roi_coordinates[0]
        x2, y2 = roi_coordinates[1]
        roi = frame[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
        cv2.imshow("ROI", roi)

        # Detect the purple object in the frame
        bbox = detect_purple_object(roi)

        # If a purple object is detected, draw a bounding box around it
        if bbox:
            x, y, w, h = bbox
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green bounding box
            print("Purple object detected at:", x, y)

        # Display the frame
        cv2.imshow("Purple Object Detection", roi)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()