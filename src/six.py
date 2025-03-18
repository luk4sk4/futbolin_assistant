import cv2

# Global variables to store ROI coordinates
roi_coordinates = []
drawing = False

# Mouse callback function
def select_roi(event, x, y, flags, param):
    global roi_coordinates, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        roi_coordinates = [(x, y)]  # Start point

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        roi_coordinates.append((x, y))  # End point
        cv2.rectangle(frame, roi_coordinates[0], roi_coordinates[1], (0, 255, 0), 2)
        cv2.imshow("Frame", frame)

# Initialize video capture
cap = cv2.VideoCapture(0)

# Create a window and set the mouse callback
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

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()