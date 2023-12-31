import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
import numpy as np
from main import get_processed_frame
from tkdial import Meter, Dial, Jogwheel
import tkinter as tk

# Set appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Constants
UPDATE_DELAY_MS = 10
ball_measurements=None
# Function to update the camera feed
def update():
    global ball_measurements
    ret, frame = cap.read()
    if ret:
        frame, ball_measurements = get_processed_frame(cap, thresholds)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        label.imgtk = imgtk
        label.configure(image=imgtk)
    label.after(UPDATE_DELAY_MS, update)

# Function to update HSV thresholds
def update_thresholds(slider_set, value_labels, indices):
    # Update value labels and thresholds
    for i, slider in enumerate(slider_set):
        value = int(slider.get())
        value_labels[i].configure(text=str(value))
        if i % 3 == 0:  # Only update thresholds at the start of each HSV set
            set_index = indices[i // 3]
            thresholds[set_index] = np.array([
                value,
                int(slider_set[i + 1].get()),
                int(slider_set[i + 2].get())
            ])

# Function to create sliders and value labels
def create_sliders(frame, labels, update_function, defaults, indices, title):
    # Create a label for the title
    title_label = ctk.CTkLabel(frame, text=title, font=("Arial", 20), fg_color=None)
    title_label.grid(row=0, columnspan=1, pady=20)  # Adjust columnspan as needed

    sliders = []
    value_labels = []
    starting_row = 1  # Start on the second row, since the title is on the first row
    for i, label in enumerate(labels):
        row = starting_row + i // 3
        label_column = (i % 3) * 2
        slider_column = label_column + 1

        slider_label = ctk.CTkLabel(frame, text=label)
        slider_label.grid(row=row, column=label_column, sticky='e', padx=5, pady=5)

        # Pass 'i' as a default argument to lambda to avoid late binding issues
        slider = ctk.CTkSlider(frame, from_=0, to=179 if 'Hue' in label else 255, command=lambda x=None, i=i: update_function(sliders, value_labels, indices))
        slider.set(defaults[i])
        slider.grid(row=row, column=slider_column, padx=5, pady=5, sticky='ew')  # Use 'ew' to expand horizontally
        sliders.append(slider)

        frame.grid_columnconfigure(label_column, weight=3)  # Give weight to label column
        frame.grid_columnconfigure(slider_column, weight=1)  # Give more weight to slider column

        # Create a label to display the value of the slider
        value_label = ctk.CTkLabel(frame, text=str(defaults[i]))
        value_label.grid(row=row, column=slider_column + 1, sticky='w', padx=5, pady=5)
        value_labels.append(value_label)

        # Add padding column for alignment if necessary
        frame.grid_columnconfigure(slider_column + 2, weight=1)

    return sliders, value_labels

# Function to toggle the visibility of slider frames
def toggle_sliders(frame_to_show):
    for frame in [ball_sliders_frame, y_axis_sliders_frame, center_sliders_frame, table_sliders_frame, robot_sliders_frame]:
        frame.pack_forget()
    frame_to_show.pack(side="top", fill="x", expand=True, padx=10, pady=10)

# Initialize the GUI
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 850)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 700)

root = ctk.CTk()
root.title("Billiard Bot")

# Load the logo image
logo_path = r"C:\Users\z3trz\Desktop\cpen 211\New folder\FilesSplit\logo.jpg"
logo_image = Image.open(logo_path)
logo_image = logo_image.resize((80, 80))  
logo_photo = ImageTk.PhotoImage(logo_image)

# Main layout frame and video label
main_frame = ctk.CTkFrame(root)
main_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

# Create the robot control frame
robot_control_frame = ctk.CTkFrame(main_frame, corner_radius=10)
robot_control_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

robot_control_frame.columnconfigure(0, weight=1)
robot_control_frame.rowconfigure(1, weight=1)

# Create the video frame within main_frame
video_frame = ctk.CTkFrame(main_frame, corner_radius=10)
video_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

# Create the top frame within video_frame
top_frame = ctk.CTkFrame(video_frame, height=100, corner_radius=10, fg_color='transparent')
top_frame.pack(side="top", fill="x", padx=10, pady=10)

# Center the logo and title within top_frame
logo_label = ctk.CTkLabel(top_frame, image=logo_photo, text="")
logo_label.image = logo_photo  
logo_label.pack(side="left", padx=10 )  # Center the logo horizontally

title_label = ctk.CTkLabel(top_frame, text="Billiard Bot", font=("Arial", 36), fg_color=None)
title_label.pack(side="left", padx=10, expand=True)  # Center the title horizontally

label = ctk.CTkLabel(video_frame, text="")
label.pack(fill="both", expand=True, padx=10, pady=10)


# Buttons frame and buttons
buttons_frame = ctk.CTkFrame(main_frame, corner_radius=10)
buttons_frame.pack(side="left", fill="y", padx=10, pady=10)

button_label = ctk.CTkLabel(buttons_frame, text="Thresholds:", font=("Arial", 24), fg_color=None)
button_label.pack(side="top", padx=50, pady=20)

button1 = ctk.CTkButton(buttons_frame, text="Ball thresholds", command=lambda: toggle_sliders(ball_sliders_frame))
button1.pack(padx=20, pady=10, fill='x')
button2 = ctk.CTkButton(buttons_frame, text="Y_axis thresholds", command=lambda: toggle_sliders(y_axis_sliders_frame))
button2.pack(padx=20, pady=10, fill='x')
button3 = ctk.CTkButton(buttons_frame, text="Center thresholds", command=lambda: toggle_sliders(center_sliders_frame))
button3.pack(padx=20, pady=10, fill='x')
button4 = ctk.CTkButton(buttons_frame, text="Table thresholds", command=lambda: toggle_sliders(table_sliders_frame))
button4.pack(padx=20, pady=10, fill='x')
button5 = ctk.CTkButton(buttons_frame, text="Robot thresholds", command=lambda: toggle_sliders(robot_sliders_frame))
button5.pack(padx=20, pady=10, fill='x')




# Sliders frames
ball_sliders_frame = ctk.CTkFrame(root)
y_axis_sliders_frame = ctk.CTkFrame(root)
center_sliders_frame = ctk.CTkFrame(root)
table_sliders_frame = ctk.CTkFrame(root)
robot_sliders_frame = ctk.CTkFrame(root)


# Slider labels and defaults
ball_labels = ["Lower Hue", "Lower Saturation", "Lower Value", "Upper Hue", "Upper Saturation", "Upper Value"]
y_axis_labels = ball_labels.copy()
center_labels = ball_labels.copy()
table_labels = ball_labels.copy()
robot_labels = ball_labels.copy()
ball_defaults = [30, 41, 110, 35, 120, 160]
y_axis_defaults = [2, 100, 100, 12, 180, 200]
center_defaults = [0, 0, 0, 179, 100, 120]
table_defaults = [0, 0, 100, 179, 40, 255]
robot_defaults = [145, 0, 30, 179, 100, 255]

# Thresholds list expanded to include center thresholds
thresholds = [np.array(ball_defaults[:3]), np.array(ball_defaults[3:]), np.array(y_axis_defaults[:3]), np.array(y_axis_defaults[3:]), np.array(center_defaults[:3]), np.array(center_defaults[3:]), np.array(table_defaults[:3]), np.array(table_defaults[3:]), np.array(robot_defaults[:3]), np.array(robot_defaults[3:])]

# Create sliders for each frame with titles
ball_sliders, ball_value_labels = create_sliders(ball_sliders_frame, ball_labels, update_thresholds, ball_defaults, [0, 1], "Ball Thresholds")
y_axis_sliders, y_axis_value_labels = create_sliders(y_axis_sliders_frame, y_axis_labels, update_thresholds, y_axis_defaults, [2, 3], "Y-Axis Thresholds")
center_sliders, center_value_labels = create_sliders(center_sliders_frame, center_labels, update_thresholds, center_defaults, [4, 5], "Center Thresholds")
table_sliders, table_value_labels = create_sliders(table_sliders_frame, table_labels, update_thresholds, table_defaults, [6, 7], "Table Thresholds")
robot_sliders, robot_value_labels = create_sliders(robot_sliders_frame, robot_labels, update_thresholds, robot_defaults, [8, 9], "Robot Thresholds")





# robot control


# Create a label for the robot control
robot_label = ctk.CTkLabel(robot_control_frame, text="Robot Control:", font=("Arial", 24), fg_color=None)
robot_label.grid(row=0, columnspan=2, padx=10, pady=20)



Num_input_container = ctk.CTkFrame(robot_control_frame, fg_color='transparent')
Num_input_container.grid(row=1, column=1, padx=10, pady=20)

sensitivity_entry = ctk.CTkEntry(Num_input_container, placeholder_text="sensitivity", width=70)
sensitivity_entry.pack(side="left", fill="both", expand=True, padx=10)

charging_time_entry = ctk.CTkEntry(Num_input_container, placeholder_text="duration", width=70)
charging_time_entry.pack(side="left", fill="both", expand=True, padx=10)

ipaddress_entry = ctk.CTkEntry(Num_input_container, placeholder_text="ip address", width=120)
ipaddress_entry.pack(side="left", fill="both", expand=True, padx=10)

controller_switch_container = ctk.CTkFrame(robot_control_frame, fg_color='transparent')
controller_switch_container.grid(row=1, column=0, padx=10, pady=20)

# Create the switch widget with a StringVar
switch_var = ctk.StringVar(value="off")
switch = ctk.CTkSwitch(controller_switch_container, text="Custom values", 
                       variable=switch_var, onvalue="on", offvalue="off")

# Place the switch in the grid, centered across both columns
switch.pack(side="left", fill="both", expand=True, padx=10)

# Create the switch widget with a StringVar
hold_var = ctk.StringVar(value="off")
hold = ctk.CTkSwitch(controller_switch_container, text="Hold", 
                       variable=hold_var, onvalue="on", offvalue="off")

# Place the switch in the grid, centered across both columns
hold.pack(side="left", fill="both", expand=True, padx=10)





text1 = ctk.CTkLabel(robot_control_frame, text="Polar coordinates", font=("Arial", 20), fg_color=None)
text1.grid(row=2, column=0,  padx=10, pady=5)

Polar_button=ctk.CTkButton(robot_control_frame, text="Send cartesian command to the robot", fg_color="#b165ff", width=280)
Polar_button.grid(row=2, column=1, padx=10, pady=20)

# Create Dial widget
dial3 = Dial(master=robot_control_frame, color_gradient=("cyan", "pink"),
             text_color="white", text="Angle: ", unit_length=10, radius=60 , start=-180, end=180)
dial3.set(center_sliders[4].get())
dial3.grid(row=3, column=0, padx=10, pady=20)

# speed
dial4 = Dial(master=robot_control_frame, color_gradient=("cyan", "pink"),
             text_color="white", text="Speed: ", unit_length=10, radius=60 , start=400, end=1500)
dial4.set(1000)
dial4.grid(row=3, column=1, padx=10, pady=20)





Polar_button_container = ctk.CTkFrame(robot_control_frame, fg_color='transparent')
Polar_button_container.grid(row=4, column=0, padx=10, pady=20)

CW_button = ctk.CTkButton(Polar_button_container, text="CW" , width=60)
CW_button.pack(side="left", fill="both", expand=True, padx=10)

CCW_button = ctk.CTkButton(Polar_button_container, text="CCW", width=60)
CCW_button.pack(side="left", fill="both", expand=True, padx=10)

Polar_slider_container = ctk.CTkFrame(robot_control_frame, fg_color='transparent')
Polar_slider_container.grid(row=4, column=1, padx=10, pady=20)

text2 = ctk.CTkLabel(Polar_slider_container, text="Distance:", fg_color=None)
text2.pack(side="left", fill="both", expand=True, padx=10)

slider_distance = ctk.CTkSlider(Polar_slider_container, from_=0, to=50, height=20)
slider_distance.pack(side="left", fill="x", expand=True, padx=10)


text3 = ctk.CTkLabel(robot_control_frame, text="Cartesian coordinates", font=("Arial", 20), fg_color=None)
text3.grid(row=5, column=0, padx=10, pady=20)

Catersian_button=ctk.CTkButton(robot_control_frame, text="Send cartesian command to the robot" , fg_color="#b165ff", width=280)
Catersian_button.grid(row=5, column=1, padx=10, pady=20)


X_button_container = ctk.CTkFrame(robot_control_frame, fg_color='transparent')
X_button_container.grid(row=6, column=0, padx=10, pady=20)

Left_button = ctk.CTkButton(X_button_container, text="Left" , width=60)
Left_button.pack(side="left", fill="both", expand=True, padx=10)

Right_button = ctk.CTkButton(X_button_container, text="Right", width=60)
Right_button.pack(side="left", fill="both", expand=True, padx=10)


X_slider_container = ctk.CTkFrame(robot_control_frame, fg_color='transparent')
X_slider_container.grid(row=6, column=1, padx=10, pady=20)

text4 = ctk.CTkLabel(X_slider_container, text="e",  fg_color=None)
text4.pack(side="left", fill="both", expand=True, padx=10)

X_direction = ctk.CTkSlider(X_slider_container, from_=-50, to=50, height=20)
X_direction.pack(side="left", fill="x", expand=True, padx=10)



Y_button_container = ctk.CTkFrame(robot_control_frame, fg_color='transparent')
Y_button_container.grid(row=7, column=0, padx=10, pady=20)

Up_button = ctk.CTkButton(Y_button_container, text="Up" , width=60)
Up_button.pack(side="left", fill="both", expand=True, padx=10)

Down_button = ctk.CTkButton(Y_button_container, text="Down", width=60)
Down_button.pack(side="left", fill="both", expand=True, padx=10)

Y_slider_container = ctk.CTkFrame(robot_control_frame, fg_color='transparent')
Y_slider_container.grid(row=7, column=1, padx=10, pady=20)

text5 = ctk.CTkLabel(Y_slider_container, text="e",  fg_color=None)
text5.pack(side="left", fill="both", expand=True, padx=10)

Y_direction = ctk.CTkSlider(Y_slider_container, from_=-50, to=50, height=20)
Y_direction.pack(side="left", fill="x", expand=True, padx=10)





# Create a button to fire the ball
fire_button = ctk.CTkButton(robot_control_frame, text="Charge and fire", fg_color="#b165ff", width=350)
fire_button.grid(row=8, column=0, columnspan=2, padx=40, pady=40)




def update_dial():
    if switch_var.get() == "off":
        if ball_measurements is not None:
            for center, radius, distance, angle, X_coordinate, Y_coordinate in ball_measurements:
                dial3.set(angle)
                slider_distance.set(distance)
                text2.configure(text=f"Distance: {distance:.1f} cm")
                text4.configure(text=f"X-direction: {X_coordinate:.1f}")
                text5.configure(text=f"Y-direction: {Y_coordinate:.1f}")
                X_direction.set(X_coordinate)
                Y_direction.set(Y_coordinate)
    # Schedule the update_dial function to be called again after 100 milliseconds
    robot_control_frame.after(100, update_dial)




    

# Call the update function initially
update_dial()


# Start the GUI
toggle_sliders(ball_sliders_frame)
update()
root.mainloop()