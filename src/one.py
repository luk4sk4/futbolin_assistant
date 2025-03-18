import cv2
import numpy as np

# Function to detect the ball and return its center coordinates
def detect_ball(frame):
    # Convert frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define range for the ball's color in HSV (adjust these values)
    lower_color = np.array([115, 100, 100])  # Lower bound for orange color
    upper_color = np.array([135, 200 , 200])  # Upper bound for orange color

    # Create a mask for the ball's color
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If contours are found, find the largest one (assumed to be the ball)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
        if radius > 10:  # Filter out small detections
            center = (int(x), int(y))
            return center, int(radius)
    return None, None

# Main function to track the ball
def track_ball():
    # Open video capture (0 for webcam, or provide a video file path)
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect the ball
        center, radius = detect_ball(frame)

        if center:
            # Draw the ball and its center
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            print(f"Ball position: {center}")  # Print the ball's position

        # Display the frame
        cv2.imshow("Ball Tracking", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

# Run the ball tracking function
track_ball()