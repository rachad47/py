import cv2
import tkinter as tk
from tkinter import ttk, Scale
from PIL import Image, ImageTk
import numpy as np
from main import get_processed_frame
import customtkinter



# Constants
UPDATE_DELAY_MS = 10

# Function to update the camera feed
def update():
    update_text_box()

    ret, frame = cap.read()
    if ret:
        # Process the frame (this is where you would include your image processing logic)
        frame,_ = get_processed_frame(cap, thresholds)  # Uncomment and use your actual processing function
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        label.imgtk = imgtk
        label.configure(image=imgtk)
    label.after(UPDATE_DELAY_MS, update)

# Function to update ball HSV values
def update_ball_thresholds(val=None):
    thresholds[0] = np.array([ball_lower_hue_slider.get(), ball_lower_saturation_slider.get(), ball_lower_value_slider.get()])
    thresholds[1] = np.array([ball_upper_hue_slider.get(), ball_upper_saturation_slider.get(), ball_upper_value_slider.get()])

# Function to update Y axis HSV values
def update_y_axis_thresholds(val=None):
    global thresholds
    thresholds[2] = np.array([y_lower_hue_slider.get(), y_lower_saturation_slider.get(), y_lower_value_slider.get()])
    thresholds[3] = np.array([y_upper_hue_slider.get(), y_upper_saturation_slider.get(), y_upper_value_slider.get()])

# Function to create sliders
def create_slider(parent_frame, text, from_, to, row, column, update_function, default_value):
    label = ttk.Label(parent_frame, text=text)
    # Place label in the specified column (0, 2, 4 for Lower and 1, 3, 5 for Upper)
    label.grid(row=row, column=column, padx=5, pady=(15,0), sticky='E')
    slider = Scale(parent_frame, from_=from_, to=to, orient="horizontal", command=update_function)
    slider.set(default_value)
    # Place slider right next to its label
    slider.grid(row=row, column=column+1, padx=5, pady=3, sticky='EW')
    return slider

def configure_sliders_frame(frame):
    for i in range(2):  # Two rows for Lower and Upper sliders
        frame.rowconfigure(i, weight=1)
    # Six columns to hold labels and sliders
    for j in range(6):
        frame.columnconfigure(j, weight=1 if j % 2 == 0 else 3)

# Function to toggle the visibility of slider frames
def toggle_sliders(set_name):
    ball_sliders_frame.pack_forget()
    y_axis_sliders_frame.pack_forget()
    if set_name == 'ball':
        ball_sliders_frame.pack(side="top", fill="x", expand=True)
    elif set_name == 'y_axis':
        y_axis_sliders_frame.pack(side="top", fill="x", expand=True)

# Event handlers for buttons
def on_button1_click():
    toggle_sliders('ball')

def on_button2_click():
    _,val = get_processed_frame(cap, thresholds)
    # print(val)
    toggle_sliders('y_axis')

def create_title_label(parent_frame, text):
    title_label = ttk.Label(parent_frame, text=text, font=('Arial', 14))
    title_label.grid(row=0, columnspan=6, pady=(0, 10))  # Span across all columns

# Function to create buttons
def create_button(parent_frame, text, command):
    button = customtkinter.CTkButton(parent_frame, text=text, command=command)
    # button = ttk.Button(parent_frame, text=text, command=command)
    button.pack(padx=5, pady=5, fill='x')
    return button

# Initialize the GUI
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

root = tk.Tk()
root.title("Camera Feed")

# Main layout frame
main_frame = ttk.Frame(root)
main_frame.pack(side="top", fill="both", expand=True)

# Frame for the video feed
video_frame = ttk.Frame(main_frame)
video_frame.pack(side="left", fill="both", expand=True)

# Video label
label = ttk.Label(video_frame)
label.pack(fill="both", expand=True)

# Frame for buttons
buttons_frame = ttk.Frame(main_frame)
buttons_frame.pack(side="left", fill="y", padx=10)

# Buttons
button1 = create_button(buttons_frame, "Ball thresholds", on_button1_click)
button2 = create_button(buttons_frame, "Y_axis thresholds", on_button2_click)



# Sliders frames
# ball_sliders_frame = ttk.Frame(root, width=root.winfo_screenwidth())
# y_axis_sliders_frame = ttk.Frame(root, width=root.winfo_screenwidth())

ball_sliders_frame = ttk.Frame(root)
y_axis_sliders_frame = ttk.Frame(root)



configure_sliders_frame(ball_sliders_frame)
configure_sliders_frame(y_axis_sliders_frame)

# Initialize lower and upper HSV values for ball and y_axis
lower_ball = np.array([30, 115, 110])
upper_ball = np.array([35, 130, 160])
lower_y_axis = np.array([2, 100, 100])
upper_y_axis = np.array([12, 180, 200])
thresholds = [lower_ball, upper_ball, lower_y_axis, upper_y_axis]



def update_text_box():
    _, val = get_processed_frame(cap, thresholds)
    text_box.delete(1.0, tk.END)  # Clear the current text
    text_box.insert(tk.END, val)  # Insert the updated text

# Add a text box below the buttons
text_box = tk.Text(buttons_frame, height=10, width=50)
text_box.pack(padx=5, pady=5)
update_text_box()



def center_sliders_frame(frame):
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(5, weight=1)
    for i in range(1, 5, 2):
        frame.grid_columnconfigure(i, weight=0)
        frame.grid_columnconfigure(i+1, weight=2)

center_sliders_frame(ball_sliders_frame)
center_sliders_frame(y_axis_sliders_frame)

# Grid configuration for ball sliders
for i in range(2):
    ball_sliders_frame.rowconfigure(i, weight=1)
    y_axis_sliders_frame.rowconfigure(i, weight=1)
for j in range(6):
    ball_sliders_frame.columnconfigure(j, weight=1)
    y_axis_sliders_frame.columnconfigure(j, weight=1)

configure_sliders_frame(ball_sliders_frame)
create_title_label(ball_sliders_frame, "Ball Sliders")  # Add title to ball sliders frame

configure_sliders_frame(y_axis_sliders_frame)
create_title_label(y_axis_sliders_frame, "Y Axis Sliders")  


ball_lower_hue_slider = create_slider(ball_sliders_frame, "Lower Hue", 0, 179, 1, 0, update_ball_thresholds, lower_ball[0])
ball_lower_saturation_slider = create_slider(ball_sliders_frame, "Lower Saturation", 0, 255, 1, 2, update_ball_thresholds, lower_ball[1])
ball_lower_value_slider = create_slider(ball_sliders_frame, "Lower Value", 0, 255, 1, 4, update_ball_thresholds, lower_ball[2])
ball_upper_hue_slider = create_slider(ball_sliders_frame, "Upper Hue", 0, 179, 2, 0, update_ball_thresholds, upper_ball[0])
ball_upper_saturation_slider = create_slider(ball_sliders_frame, "Upper Saturation", 0, 255, 2, 2, update_ball_thresholds, upper_ball[1])
ball_upper_value_slider = create_slider(ball_sliders_frame, "Upper Value", 0, 255, 2, 4, update_ball_thresholds, upper_ball[2])

y_lower_hue_slider = create_slider(y_axis_sliders_frame, "Lower Hue", 0, 179, 1, 0, update_y_axis_thresholds, lower_y_axis[0])
y_lower_saturation_slider = create_slider(y_axis_sliders_frame, "Lower Saturation", 0, 255, 1, 2, update_y_axis_thresholds, lower_y_axis[1])
y_lower_value_slider = create_slider(y_axis_sliders_frame, "Lower Value", 0, 255, 1, 4, update_y_axis_thresholds, lower_y_axis[2])
y_upper_hue_slider = create_slider(y_axis_sliders_frame, "Upper Hue", 0, 179, 2, 0, update_y_axis_thresholds, upper_y_axis[0])
y_upper_saturation_slider = create_slider(y_axis_sliders_frame, "Upper Saturation", 0, 255, 2, 2, update_y_axis_thresholds, upper_y_axis[1])
y_upper_value_slider = create_slider(y_axis_sliders_frame, "Upper Value", 0, 255, 2, 4, update_y_axis_thresholds, upper_y_axis[2])

# Initially show ball sliders
toggle_sliders('ball')

# Start the GUI
update()
root.mainloop()
