import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import ttk
import threading
import queue
import os

start_time = time.time()

roi_coordinates = []
drawing = False
frame = None  # Initialize frame variable
probability = 50
time_in_cuadrants = [250, 250, 250, 250, 250, 250]
goals = [0, 0]
team_a_prob, team_b_prob = 50, 50


def add_player(event=None):  # Added event=None to make it callable without event
    new_player = new_player_entry.get().strip()  # Added strip() to remove whitespace
    if new_player and new_player not in all_values:
        all_values.append(new_player)
        try:
            with open("../data/players.txt", "a") as file:
                file.write("\n" + new_player)  # Add a newline before the new player
        except FileNotFoundError:
            # Handle case where directory doesn't exist
            os.makedirs("../data", exist_ok=True)
            with open("../data/players.txt", "a") as file:
                file.write("\n" + new_player)  # Add a newline before the new player
        
        # Update dropdown values
        updated_values = ["defensa", "delantero"] + all_values  # Common base values
        dropdown1['values'] = updated_values
        dropdown2['values'] = updated_values
        dropdown3['values'] = updated_values
        dropdown4['values'] = updated_values
        
        new_player_entry.delete(0, tk.END)  # Clear the entry field



# Function to simulate updating variables in a worker thread
def worker_thread_func(data_queue, ):
    while True:
        # Simulate updating variables
        time_elapsed = f"{int(time.time() - start_time) // 60:02d}:{int(time.time() - start_time) % 60:02d}"
        
        global team_a_prob, team_b_prob, goals

        # Put the updated data in the queue
        data_queue.put((goals, time_elapsed, team_a_prob, team_b_prob))

        # Simulate a delay (e.g., 1 second)
        time.sleep(1)

# Function to update the GUI with data from the queue
def update_gui():
    try:
        # Get the latest data from the queue
        goals, time_elapsed, team_a_prob, team_b_prob = data_queue.get_nowait()

        # Update the labels
        goal_a_label.config(text=f"{goals[0]}")
        goal_b_label.config(text=f"{goals[1]}")
        time_label.config(text=f"{time_elapsed}")
        team_a_prob_label.config(text=f"{team_a_prob:.2f}%")
        team_b_prob_label.config(text=f"{team_b_prob:.2f}%")
    except queue.Empty:
        pass  # No new data in the queue

    # Schedule the next update
    root.after(100, update_gui)  # Check the queue every 100 ms

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

    a_modification = 1 + 1/10 * goals[0] - 1/10 * goals[1] + 1/10 * goals[0] * goals[0] - 1/10 * goals[1] * goals[1]
    b_modification = 1 + 1/10 * goals[1] - 1/10 * goals[0] + 1/10 * goals[1] * goals[1] - 1/10 * goals[0] * goals[0]

    print(a_modification, b_modification, team_a_ponderated, team_b_ponderated, total_ponderated)
    # Calculate probabilities
    team_a_prob = (team_a_ponderated * a_modification / total_ponderated) * 100
    team_b_prob = (team_b_ponderated * b_modification / total_ponderated) * 100

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

# Function to run OpenCV processing in a separate thread
def opencv_thread_func():
    global frame
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
            six_x = roi.shape[1] // 6  # Second x-coordinate
            mid_y = roi.shape[0] // 2  # Middle y-coordinate

            # Draw vertical lines in the ROI
            cv2.line(roi, (mid_x, 0), (mid_x, roi.shape[0]), (255, 0, 0), 2)  # Blue vertical line
            cv2.line(roi, (six_x, 0), (six_x, roi.shape[0]), (255, 0, 0), 2)  # Blue vertical line
            cv2.line(roi, (2 * six_x, 0), (2 * six_x, roi.shape[0]), (255, 0, 0), 2)  # Blue vertical line
            cv2.line(roi, (4 * six_x, 0), (4 * six_x, roi.shape[0]), (255, 0, 0), 2)  # Blue vertical line
            cv2.line(roi, (5 * six_x, 0), (5 * six_x, roi.shape[0]), (255, 0, 0), 2)  # Blue vertical line

            cuadrant = None
            # Detect in which quadrant the object is
            if bbox:
                if center[0] < six_x:
                    cuadrant = 0
                    cv2.putText(roi, "First Cuadrant", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif center[0] > six_x and center[0] < (2 * six_x):
                    cuadrant = 1
                    cv2.putText(roi, "Second Cuadrant", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif center[0] > (2 * six_x) and center[0] < mid_x:
                    cuadrant = 2
                    cv2.putText(roi, "Third Cuadrant", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif center[0] > mid_x and center[0] < (4 * six_x):
                    cuadrant = 3
                    cv2.putText(roi, "Fourth Cuadrant", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif center[0] > (4 * six_x) and center[0] < (5 * six_x):
                    cuadrant = 4
                    cv2.putText(roi, "Fifth Cuadrant", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    cuadrant = 5
                    cv2.putText(roi, "Sixth Cuadrant", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Display the frame
                print("coordinates:", center, "cuadrant: ", cuadrant)

                update_quadrant_time(cuadrant)

                global team_a_prob, team_b_prob, goals, start_time, time_in_cuadrants
                team_a_prob, team_b_prob = calculate_win_probabilities(time_in_cuadrants)

                print("goals: ", goals)

            cv2.imshow("Purple Object Detection", roi)

        # Exit if 'q' is pressed
        key = cv2.waitKey(1) & 0xFF

        # Update goals based on key press
        if key == ord('1'):
            goals[0] += 1
            print("GOAL TEAM A")
        elif key == ord('2'):
            goals[1] += 1
            print("GOAL TEAM B")
        elif key == ord('0'):
            #save data to a file
            with open("../data/match_data.txt", "a") as file:  # Use "a" to append to the file
                file.write(f"Time: {int(time.time() - start_time) // 60:02d}:{int(time.time() - start_time) % 60:02d}\n")
                file.write(f"Goals: Team A - {goals[0]}, Team B - {goals[1]}\n")
                file.write(f"Time in Cuadrants: {time_in_cuadrants}\n")
                #i need to save the players names
                file.write(f"Players team A: {dropdown_var1.get()}, {dropdown_var2.get()}. Players team B:{dropdown_var3.get()}, {dropdown_var4.get()}\n")
                file.write("-" * 40 + "\n")  # Separator for each game
            
            goals = [0, 0]
            time_in_cuadrants = [250, 250, 250, 250, 250, 250]
            team_a_prob, team_b_prob = 50, 50
            start_time = time.time()
            
            
            print("reset")
        elif key == ord('q'):
            break

    # Release the video capture and close all windows
    cap.release()
    cv2.destroyAllWindows()


#all values is the list of values saved on /data/players.txt
all_values = []
with open("../data/players.txt", "r") as file:
    for line in file:
        all_values.append(line.strip())  # Remove newline characters and spaces

# Create the main Tkinter window
root = tk.Tk()
root.title("Futbolín Match Stats")
root.geometry("1100x800")  # Set window size

# Create a queue to share data between threads
data_queue = queue.Queue()

# Create and style labels
style = ttk.Style()
style.configure("TLabel", font=("Arial", 100), background="#f0f0f0", foreground="#333333", padding=10)

time_label = ttk.Label(root, text="00:00", style="TLabel")
time_label.grid(row=0, column=0, columnspan=4, pady=10)

nameA_label = ttk.Label(root, text="TEAM A", style="TLabel")
nameA_label.grid(row=1, column=0, columnspan=2, padx=20)

dropdown_var1 = tk.StringVar(value="defensa")  # Default value is "defensa"
dropdown1 = ttk.Combobox(root, textvariable=dropdown_var1, font=("Arial", 20), justify="center")
dropdown1['values'] = ["defensa"] + all_values  # Include "defensa" as an option
dropdown1['state'] = 'readonly'  # Make it read-only
dropdown1.grid(row=2, column=0, padx=20, pady=10)

dropdown_var2 = tk.StringVar(value="delantero")  # Default value is "defensa"
dropdown2 = ttk.Combobox(root, textvariable=dropdown_var2, font=("Arial", 20), justify="center")
dropdown2['values'] = ["delantero"] + all_values  # Include "defensa" as an option
dropdown2['state'] = 'readonly'  # Make it read-only
dropdown2.grid(row=3, column=0, padx=20, pady=10)

goal_a_label = ttk.Label(root, text="0", style="TLabel")
goal_a_label.grid(row=2, rowspan=2, column=1, padx=20)

nameB_label = ttk.Label(root, text="TEAM B", style="TLabel")
nameB_label.grid(row=1, column=2, columnspan=2, padx=20)

goal_b_label = ttk.Label(root, text="0", style="TLabel")
goal_b_label.grid(row=2, rowspan=2, column=2, padx=20)

dropdown_var3 = tk.StringVar(value="defensa")  # Default value is "defensa"
dropdown3 = ttk.Combobox(root, textvariable=dropdown_var3, font=("Arial", 20), justify="center")
dropdown3['values'] = ["defensa"] + all_values  # Include "defensa" as an option
dropdown3['state'] = 'readonly'  # Make it read-only
dropdown3.grid(row=2, column=3, padx=20, pady=10)

dropdown_var4 = tk.StringVar(value="delantero")  # Default value is "defensa"
dropdown4 = ttk.Combobox(root, textvariable=dropdown_var4, font=("Arial", 20), justify="center")
dropdown4['values'] = ["delantero"] + all_values  # Include "defensa" as an option
dropdown4['state'] = 'readonly'  # Make it read-only
dropdown4.grid(row=3, column=3, padx=20, pady=10)

team_a_prob_label = ttk.Label(root, text="50.00%", style="TLabel")
team_a_prob_label.grid(row=4, column=0, columnspan=2, padx=20)

team_b_prob_label = ttk.Label(root, text="50.00%", style="TLabel")
team_b_prob_label.grid(row=4, column=2, columnspan=2, padx=20)

new_player_label = ttk.Label(root, text="Add Player:", font=("Arial", 20))
new_player_label.grid(row=5, column=0, padx=20, pady=10)

# Add the place where you can write the name of the player
new_player_entry = ttk.Entry(root, font=("Arial", 20))
new_player_entry.grid(row=5, column=1, padx=20, pady=10)

# Bind the Enter key to the add_player function
new_player_entry.bind('<Return>', add_player)



# Start the worker thread
worker_thread = threading.Thread(target=worker_thread_func, args=(data_queue, ))
worker_thread.daemon = True  # Daemonize the thread so it exits when the main program exits
worker_thread.start()

# Start the OpenCV thread
opencv_thread = threading.Thread(target=opencv_thread_func)
opencv_thread.daemon = True  # Daemonize the thread so it exits when the main program exits
opencv_thread.start()

# Start updating the GUI
root.after(100, update_gui)  # Initial call to start the update loop

# Run the Tkinter event loop
root.mainloop()