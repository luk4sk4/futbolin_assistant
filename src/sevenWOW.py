import cv2
import numpy as np
import time

start_time = time.time()

roi_coordinates = []
drawing = False
frame = None  # Initialize frame variable
probability = 50
time_in_cuadrants = [250, 250, 250, 250, 250, 250]
goals = [0, 0]


# Function to update quadrant time
def update_quadrant_time(quadrant):
    global time_in_cuadrants
    
    
    time_in_cuadrants[quadrant] += 1

# Function to calculate winning probabilities
def calculate_win_probabilities(time_in_cuadrants):
    total_time = sum(time_in_cuadrants)
    if total_time == 0:
        return 0.5, 0.5  # Default to equal probability if no time has passed


    # Calculate ponderated time for each team (1 for forwards, 0.5 for backwards and midfielders)
    
    team_a_ponderated = time_in_cuadrants[0] * 0.5 + time_in_cuadrants[2] * 0.5 + time_in_cuadrants[4] * 1
    team_b_ponderated = time_in_cuadrants[5] * 0.5 + time_in_cuadrants[3] * 0.5 + time_in_cuadrants[1] * 1
    total_ponderated = team_a_ponderated + team_b_ponderated

    a_modification = 1+1/10*goals[0]-1/10*goals[1]+1/10*goals[0]*goals[0]-1/10*goals[1]*goals[1]
    b_modification = 1+1/10*goals[1]-1/10*goals[0]+1/10*goals[1]*goals[1]-1/10*goals[0]*goals[0]
    
    print(a_modification, b_modification, team_a_ponderated, team_b_ponderated, total_ponderated)
    # Calculate probabilities
    team_a_prob =  (team_a_ponderated * a_modification / total_ponderated) 
    team_b_prob =  (team_b_ponderated * b_modification / total_ponderated)
    
    
    print(team_a_prob, team_b_prob, team_a_ponderated * a_modification, team_b_ponderated * b_modification)

    return team_a_prob, team_b_prob

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

        # Detect the purple object in the frame
        bbox = detect_purple_object(roi)

        # If a purple object is detected, draw a bounding box around it
        if bbox:
            x, y, w, h = bbox
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green bounding box
            center = (x + w // 2, y + h // 2)  # Center of the bounding box
            cv2.circle(roi, center, 2, (0, 255, 0), -1)  # Green dot
            
        # Calculate the midpoint of the ROI
        mid_x = roi.shape[1] // 2  # Middle x-coordinate
        six_x = roi.shape[1] // 6 # Second x-coordinate
        mid_y = roi.shape[0] // 2  # Middle y-coordinate

        # Draw a vertical line in the middle of the ROI
        cv2.line(roi, (mid_x, 0), (mid_x, roi.shape[0]), (255, 0, 0), 2)  # Blue vertical line
        cv2.line(roi, (six_x, 0), (six_x, roi.shape[0]), (255, 0, 0), 2)  # Blue vertical line
        cv2.line(roi, (2*six_x, 0), (2*six_x, roi.shape[0]), (255, 0, 0), 2)  # Blue vertical line
        cv2.line(roi, (4*six_x, 0), (4*six_x, roi.shape[0]), (255, 0, 0), 2)  # Blue vertical line
        cv2.line(roi, (5*six_x, 0), (5*six_x, roi.shape[0]), (255, 0, 0), 2)  # Blue vertical line
        
        cuadrant = None
        #detect in which cuadrant the object is
        if bbox:
            if center[0] < six_x:
                cuadrant = 0
                cv2.putText(roi, "First Cuadrant", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif center[0] > six_x and center[0] < (2*six_x):
                cuadrant = 1
                cv2.putText(roi, "Second Cuadrant", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif center[0] > (2*six_x) and center[0] < mid_x:
                cuadrant = 2
                cv2.putText(roi, "Third Cuadrant", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif center[0] > mid_x and center[0] < (4*six_x):
                cuadrant = 3
                cv2.putText(roi, "Fourth Cuadrant", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif center[0] > (4*six_x) and center[0] < (5*six_x):
                cuadrant = 4
                cv2.putText(roi, "Fifth Cuadrant", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cuadrant = 5
                cv2.putText(roi, "Sixth Cuadrant", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
            # Display the frame
            print("coordinates:", center, "cuadrant: ", cuadrant)
            
            update_quadrant_time(cuadrant)
            
            team_a_prob, team_b_prob = calculate_win_probabilities(time_in_cuadrants)
            print(f"TEAM A Winning Probability: {team_a_prob * 100:.2f}%")
            print(f"TEAM B Winning Probability: {team_b_prob * 100:.2f}%")
            
            print("goals: ", goals)
        
        

        
        
        cv2.imshow("Purple Object Detection", roi)
        #show a screen with the varaibles GOAL, TIME, TEAM_A_PROB AND TEAM_B_PROB withou using cv2.imshow
        

    # Exit if 'q' is pressed
    key = cv2.waitKey(1) & 0xFF

    # Cambia la variable `modo` según la tecla presionada
    if key == ord('1'):
        goals[0] += 1
        print("GOAL TEAM A")
    elif key == ord('2'):
        goals[1] += 1
        print("GOAL TEAM B")
    elif key == ord('0'):
        goals = [0, 0]
        print("reset")
    elif key == ord('q'):
        break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()