import tkinter as tk
from tkinter import ttk
import threading
import queue
import time
import random

# Function to simulate updating variables in a worker thread
def worker_thread_func(data_queue):
    while True:
        # Simulate updating variables
        goals = [random.randint(0, 10), random.randint(0, 10)]
        time_elapsed = f"{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
        team_a_prob = random.uniform(0, 100)
        team_b_prob = 100 - team_a_prob

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
time_label.grid(row=0, column=0, columnspan=3, pady=10)

nameA_label = ttk.Label(root, text="TEAM A", style="TLabel")
nameA_label.grid(row=1, column=0, padx=20)

goal_a_label = ttk.Label(root, text="0", style="TLabel")
goal_a_label.grid(row=2, column=0, padx=20)

nameB_label = ttk.Label(root, text="TEAM B", style="TLabel")
nameB_label.grid(row=1, column=2, padx=20)

goal_b_label = ttk.Label(root, text="0", style="TLabel")
goal_b_label.grid(row=2, column=2, padx=20)

team_a_prob_label = ttk.Label(root, text="50.00%", style="TLabel")
team_a_prob_label.grid(row=3, column=0, padx=20)

team_b_prob_label = ttk.Label(root, text="50.00%", style="TLabel")
team_b_prob_label.grid(row=3, column=2, padx=20)

# Start the worker thread
worker_thread = threading.Thread(target=worker_thread_func, args=(data_queue,))
worker_thread.daemon = True  # Daemonize the thread so it exits when the main program exits
worker_thread.start()

# Start updating the GUI
root.after(100, update_gui)  # Initial call to start the update loop

# Run the Tkinter event loop
root.mainloop()