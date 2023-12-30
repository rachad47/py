import cv2
import numpy as np
import threading
import time
from image_processing import detect_backgroud_boudary, detect_pink_paper, detect_colored_spots, detect_colored_spots2, detect_balls
from utility_functions import create_click_event, detect_and_draw_Y_axis, calculate_center, calculate_ball_measurements, annotate_ball_measurements
from robot_control import send_command, calculate_rotation_steps, calculate_translation_steps, send_strike_command
from constants import MOTOR_SPEED, LOWER_CENTER , UPPER_CENTER, LOWER_Y_AXIS, UPPER_Y_AXIS, LOWER_BALL, UPPER_BALL


# Capture video from webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
# cap.set(cv2.CAP_PROP_FPS, 10)

while True:
    ret, frameOrigin = cap.read()
    if not ret:
        break
    
    # Blur the frame to reduce noise
    frame = cv2.GaussianBlur(frameOrigin, (5,5), 0)
    table_contour = detect_backgroud_boudary(frame)

    if table_contour is not None:
        table_mask = np.zeros_like(frame[:, :, 0])
        cv2.drawContours(table_mask, [table_contour], -1, 255, -1)
        pink_paper_box = detect_pink_paper(frame, table_mask)

        origin = None  # Initialize the origin

        if pink_paper_box is not None:
            pink_paper_mask = np.zeros_like(frame[:, :, 0])
            cv2.drawContours(pink_paper_mask, [pink_paper_box], 0, 255, -1)  # note that here we are drawing the box on the mask

            # Detect the black spot as the origin of our coordinate system
            center_spot=detect_colored_spots(frame, (LOWER_CENTER , UPPER_CENTER ), pink_paper_mask)
            if center_spot:
                origin = calculate_center(center_spot[0])
                cv2.circle(frame, origin, 5, (0, 0, 255), -1)

            # Detect the yellow spot so that from the center to the yellow spot is the Y-axis   
            y_direction = detect_and_draw_Y_axis(frame, (LOWER_Y_AXIS , UPPER_Y_AXIS ), pink_paper_mask, origin)

        # Detect balls
        if origin is not None and y_direction is not None:

            balls = detect_balls(frame, table_contour, (LOWER_BALL , UPPER_BALL ))
            ball_measurements = calculate_ball_measurements(frame, balls, origin, y_direction)

            # Drawing and annotations
            annotate_ball_measurements(frame, ball_measurements, origin)

    
    cv2.imshow('Frame', frame)
    cv2.setMouseCallback('Frame', create_click_event(frame))


    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        print("Quitting")
        break
    
    elif key & 0xFF == ord('h'):
        # Save the current measuraments to print later 
        cv2.imshow('hold', frame)
        hold_measurement = ball_measurements
        
    #Polar coordinates
    elif key & 0xFF == ord('p'):
        if 'hold_measurement' in locals():
            for center, radius, distance, angle, X_coordinate, Y_coordinate in hold_measurement:
                print(f"Distance = {distance:.1f} cm, Angle = {angle:.1f} degrees")

            rotation_steps = -calculate_rotation_steps(angle)
            translation_steps = calculate_translation_steps(distance/100)-100

            print(f"Rotation Steps: {rotation_steps}, Translation Steps: {translation_steps}")

            send_command(rotation_steps, MOTOR_SPEED, rotation_steps, MOTOR_SPEED, rotation_steps, MOTOR_SPEED)
            threading.Thread(target=lambda: (time.sleep(2), send_command(translation_steps, MOTOR_SPEED, 0, MOTOR_SPEED, -translation_steps, MOTOR_SPEED))).start()


    #Cartesian coordinates
    elif key & 0xFF == ord('c'):
        if 'hold_measurement' in locals():
            for center, radius, distance, angle, X_coordinate, Y_coordinate in hold_measurement:
                print(f"X_coordinate = {X_coordinate:.1f} cm, Y_coordinate = {Y_coordinate:.1f} cm")
                # send_strike_command(1500) 


cap.release()
cv2.destroyAllWindows()