import cv2
import numpy as np

# Function to detect purple squares
def detect_purple_squares(frame):
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the range for purple color in HSV
    lower_purple = np.array([130, 50, 50])  # Lower bound for purple
    upper_purple = np.array([160, 255, 255])  # Upper bound for purple

    # Create a mask for the purple color
    mask = cv2.inRange(hsv, lower_purple, upper_purple)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Get the bounding boxes of the purple squares
    purple_squares = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        purple_squares.append((x, y, w, h))

    return purple_squares

# Function to check if a point is inside a rectangle
def is_point_inside_rectangle(point, rect):
    x, y = point
    rx, ry, rw, rh = rect
    return rx <= x <= rx + rw and ry <= y <= ry + rh

# Initialize the video capture
cap = cv2.VideoCapture(0)  # Use 0 for the default camera

while True:
    # Read a new frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture video")
        break

    # Detect the purple squares
    purple_squares = detect_purple_squares(frame)

    # If exactly four purple squares are found, define the ROI
    if len(purple_squares) == 4:
        # Sort the squares to identify the corners (top-left, top-right, bottom-left, bottom-right)
        purple_squares.sort(key=lambda x: (x[1], x[0]))  # Sort by y, then x
        top_left = purple_squares[0]
        top_right = purple_squares[1]
        bottom_left = purple_squares[2]
        bottom_right = purple_squares[3]

        # Define the rectangle ROI using the four corners
        roi_x = top_left[0]
        roi_y = top_left[1]
        roi_width = bottom_right[0] - top_left[0]
        roi_height = bottom_right[1] - top_left[1]

        # Draw the rectangle ROI
        cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)

        # Detect the object inside the ROI (for example, a red object)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 50, 50])  # Lower bound for red
        upper_red = np.array([10, 255, 255])  # Upper bound for red
        red_mask = cv2.inRange(hsv, lower_red, upper_red)
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Check if any red object is inside the ROI
        for contour in red_contours:
            x, y, w, h = cv2.boundingRect(contour)
            object_center = (x + w // 2, y + h // 2)  # Center of the object

            # Check if the object is inside the rectangle
            if is_point_inside_rectangle(object_center, (roi_x, roi_y, roi_width, roi_height)):
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Draw red bounding box
                cv2.putText(frame, "Object Inside ROI", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow("Object Detection", frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()