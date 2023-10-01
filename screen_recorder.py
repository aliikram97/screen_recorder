import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
import threading
import pyautogui

global frame_count
frame_count = 0
global counter
counter = 0
global r
r = [int(0), int(0), int(0), int(0)]
global resolution
resolution = (1920, 1080)  # Set initial resolution

# Create a flag to control recording
recording = False
out = cv2.VideoWriter('recording.avi', cv2.VideoWriter_fourcc(*'MJPG'), 15, resolution)
def start():
    global recording
    recording = True
    # Disable the "Start" button after starting recording
    start_button.config(state=tk.DISABLED)
    # Enable the "Pause" and "Stop" buttons
    pause_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.NORMAL)

def stop():
    global recording
    recording = False
    out.release()  # Release the VideoWriter when stopping recording
    control.destroy()

def pause():
    global recording
    recording = False
    # Enable the "Start" button when paused
    start_button.config(state=tk.NORMAL)
    # Disable the "Pause" button while paused
    pause_button.config(state=tk.DISABLED)
    # Enable the "Stop" button when paused
    stop_button.config(state=tk.NORMAL)

def crop():
    global crop_var, r
    crop_var.set(True)
    print(crop_var)
    option.destroy()
    if crop_var.get():
        img = pyautogui.screenshot()
        frame = np.array(img)
        r = cv2.selectROI("Select the area", frame)
        cv2.destroyAllWindows()
    open_control_window()

def fullscreen():
    global fullscreen_var
    fullscreen_var.set(True)
    option.destroy()
    open_control_window()

def open_control_window():
    global control, recording, start_button, pause_button, stop_button
    control = tk.Tk()
    control.title("Controls")
    control.geometry('400x100')

    recording = False  # Reset the recording flag when the control window is opened

    start_button = ttk.Button(control, text="Start", command=start)
    start_button.pack(padx=10)
    pause_button = ttk.Button(control, text="Pause", command=pause, state=tk.DISABLED)
    pause_button.pack(padx=10)
    stop_button = ttk.Button(control, text="Stop", command=stop, state=tk.DISABLED)
    stop_button.pack(padx=10)

    control.after(1, ScreenRecorder)

    control.mainloop()

def highlight_recording_area():
    global r

    while recording:
        x, y, width, height = r
        img = pyautogui.screenshot()
        frame = np.array(img)

        # Draw a red rectangle on the screenshot to highlight the recording area
        frame[y:y+height, x:x+width, :] = [0, 0, 255]  # Red channel

        # Convert frame to RGB format for displaying with OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Display the frame with the highlighted area
        cv2.imshow('Recording', frame)
        cv2.waitKey(1)

def ScreenRecorder():
    global frame_count, counter, resolution, recording, r, crop_var, fullscreen_var, out

    if recording:
        # Take screenshot using PyAutoGUI
        img = pyautogui.screenshot()

        # Convert the screenshot to a numpy array
        frame = np.array(img)

        if crop_var.get():
            frame = frame[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]

        frame = cv2.resize(frame, resolution, interpolation=cv2.INTER_NEAREST)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        print('recording')
        out.write(frame)
        frame_count += 1
        counter += 1
        print(counter)

    option.after(1, ScreenRecorder)

option = tk.Tk()
option.title("Option")
option.geometry('400x100')

crop_var = tk.BooleanVar()
crop_var.set(False)
fullscreen_var = tk.BooleanVar()
fullscreen_var.set(True)

crop_button = ttk.Button(option, text="Crop", command=crop)
crop_button.pack(padx=10)
fullscreen_button = ttk.Button(option, text="Full Screen", command=fullscreen)
fullscreen_button.pack(padx=10)

# Create a thread to highlight the recording area
highlight_thread = threading.Thread(target=highlight_recording_area)
highlight_thread.daemon = True  # Allow the thread to exit when the main program exits
highlight_thread.start()

option.mainloop()
cv2.destroyAllWindows()
