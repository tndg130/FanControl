#fan_control_gui.py

import os
import sys
import tkinter as tk
from gpiozero import OutputDevice
import subprocess
import atexit
import re

# Define paths for socket and restore files
SOCKET_FILE = "/tmp/fan_control_socket"
RESTORE_FILE = "/tmp/fan_control_restore"

# Check if another instance of the fan control GUI is already running
if os.path.exists(SOCKET_FILE):
    try:
        # Read the PID of the running instance from the socket file
        with open(SOCKET_FILE, "r") as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)  # Try to send a signal to the process (checks if it's alive)
        print("Fan Control GUI is already running. Restoring window...")
        with open(RESTORE_FILE, "w") as f:
            f.write("restore")  # Write "restore" to the restore file
        sys.exit()  # Exit this instance since the GUI is already running
    except (OSError, ValueError):
        # If an error occurs (e.g., the process is not running), remove the stale socket file
        print("Removing stale socket file.")
        os.remove(SOCKET_FILE)

# Function to check if a restore request exists
def check_for_restore():
    """Check if the restore request exists and restore the window if needed"""
    if os.path.exists(RESTORE_FILE):
        os.remove(RESTORE_FILE)  # Remove restore file after processing
        root.deiconify()  # Show the window if it was minimized
        print("Window restored")
    root.after(1000, check_for_restore)  # Check again in 1 second

# Write the current process ID (PID) to the socket file
with open(SOCKET_FILE, "w") as f:
    f.write(str(os.getpid()))

# Register cleanup function to run on exit
def cleanup():
    """Remove socket and restore files on exit"""
    if os.path.exists(SOCKET_FILE):
        os.remove(SOCKET_FILE)
    if os.path.exists(RESTORE_FILE):
        os.remove(RESTORE_FILE)

atexit.register(cleanup)  # Register cleanup function to run when the program ends

# Configuration variables
fan = OutputDevice(23)  # GPIO pin 23 to control the fan
TEMP_ON_THRESHOLD = 65.0  # Temperature threshold to turn the fan ON
TEMP_OFF_THRESHOLD = 35.0  # Temperature threshold to turn the fan OFF
fan_on = False  # Flag to track if the fan is on
keep_fan_off = False  # Flag to track if the fan should remain off regardless of temperature

# Function to get the CPU temperature using vcgencmd
def get_cpu_temperature():
    try:
        result = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)
        # Extract temperature value from the output
        temp_str = result.stdout.strip().replace("temp=", "").replace("C", "").replace("'", "").strip()
        return float(temp_str)
    except Exception as e:
        print(f"Error getting temperature: {e}")
        return None

# Function to update temperature and control the fan based on thresholds
def update_temperature():
    global fan_on, keep_fan_off
    temp = get_cpu_temperature()  # Get the current CPU temperature
    
    if temp is not None:
        # Update the displayed temperature in the GUI
        current_temp_label.config(text=f"Temp: {temp:.1f}")

        if keep_fan_off:
            print("Fan is set to remain OFF")
            return  # Do nothing if the fan should remain off

        # If temperature exceeds the ON threshold and the fan is off, turn the fan on
        if temp >= TEMP_ON_THRESHOLD and not fan_on:
            fan.on()
            fan_on = True
            print("High temp, Fan ON")
        
        # If temperature drops below the OFF threshold and the fan is on, turn the fan off
        elif temp <= TEMP_OFF_THRESHOLD and fan_on:
            fan.off()
            fan_on = False
            print("Temp is cool, Fan OFF")
    
    root.after(5000, update_temperature)  # Check the temperature every 5 seconds

# Function to manually turn on the fan
def turn_on_fan():
    global fan_on
    fan.on()
    fan_on = True
    print("Fan ON manually")

# Function to manually turn off the fan
def turn_off_fan():
    global fan_on
    fan.off()
    fan_on = False
    print("Fan OFF manually")

# Function to handle the window closing event
def on_closing():
    root.withdraw()  # Minimize the window instead of closing
    print("Fan Control running in background.")

# Function to update the temperature thresholds from the input fields
def set_thresholds():
    global TEMP_ON_THRESHOLD, TEMP_OFF_THRESHOLD
    try:
        # Read the values from the entry fields
        TEMP_ON_THRESHOLD = float(on_threshold_entry.get())
        TEMP_OFF_THRESHOLD = float(off_threshold_entry.get())

        # Update the script file with the new thresholds
        script_file = os.path.abspath(__file__)
        with open(script_file, "r") as f:
            content = f.read()
        # Replace the old threshold values with the new ones
        content = re.sub(r'TEMP_ON_THRESHOLD = \d+(\.\d+)?', f'TEMP_ON_THRESHOLD = {TEMP_ON_THRESHOLD}', content)
        content = re.sub(r'TEMP_OFF_THRESHOLD = \d+(\.\d+)?', f'TEMP_OFF_THRESHOLD = {TEMP_OFF_THRESHOLD}', content)
        with open(script_file, "w") as f:
            f.write(content)

        print(f"Updated thresholds - ON: {TEMP_ON_THRESHOLD}, OFF: {TEMP_OFF_THRESHOLD}")
    except ValueError:
        print("Invalid threshold values")  # Handle invalid input

# Function to toggle the fan's "keep off" state (prevent automatic fan control)
def toggle_keep_fan_off():
    global keep_fan_off
    keep_fan_off = not keep_fan_off
    if keep_fan_off:
        fan.off()  # Turn the fan off if it's set to remain off
        print("Fan will remain OFF until disabled")
        keep_fan_off_button.config(text="Resume Auto")  # Update button text
    else:
        print("Auto fan control resumed")
        keep_fan_off_button.config(text="Keep OFF")  # Update button text

# Create the main window using Tkinter
root = tk.Tk()
root.title("Fan Control")  # Set window title
root.protocol("WM_DELETE_WINDOW", on_closing)  # Handle window close event

# Position window at top-right corner of the screen
screen_width = root.winfo_screenwidth()
root.geometry(f"+{screen_width - 220}+10")

# Create and display the current temperature label
current_temp_label = tk.Label(root, text="Temp: --", font=("Arial", 10))
current_temp_label.pack(pady=2)

# Create a frame for input fields to set the temperature thresholds
threshold_frame = tk.Frame(root)
threshold_frame.pack(pady=2)

# Label and entry for "ON" threshold
tk.Label(threshold_frame, text="ON:", font=("Arial", 10)).grid(row=0, column=0, padx=2)
on_threshold_entry = tk.Entry(threshold_frame, font=("Arial", 10), width=5)
on_threshold_entry.insert(0, str(TEMP_ON_THRESHOLD))  # Set default value
on_threshold_entry.grid(row=0, column=1, padx=2)

# Label and entry for "OFF" threshold
tk.Label(threshold_frame, text="OFF:", font=("Arial", 10)).grid(row=0, column=2, padx=2)
off_threshold_entry = tk.Entry(threshold_frame, font=("Arial", 10), width=5)
off_threshold_entry.insert(0, str(TEMP_OFF_THRESHOLD))  # Set default value
off_threshold_entry.grid(row=0, column=3, padx=2)

# Button to update thresholds
set_button = tk.Button(root, text="Set", font=("Arial", 10), width=7, command=set_thresholds)
set_button.pack(pady=2)

# Frame for manual fan control buttons
control_frame = tk.Frame(root)
control_frame.pack(pady=2)

# Button to manually turn the fan ON
manual_on_button = tk.Button(control_frame, text="ON", font=("Arial", 10), width=5, command=turn_on_fan)
manual_on_button.grid(row=0, column=0, padx=3)

# Button to manually turn the fan OFF
manual_off_button = tk.Button(control_frame, text="OFF", font=("Arial", 10), width=5, command=turn_off_fan)
manual_off_button.grid(row=0, column=1, padx=3)

# Button to toggle the "keep fan off" feature
keep_fan_off_button = tk.Button(root, text="Keep OFF", font=("Arial", 10), width=12, command=toggle_keep_fan_off)
keep_fan_off_button.pack(pady=5)

# Start the temperature update loop
update_temperature()

# Start the restore check loop
check_for_restore()

# Run the Tkinter main loop
root.mainloop()
