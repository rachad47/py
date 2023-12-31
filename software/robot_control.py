import requests
import numpy as np
import math
from constants import esp32_ip, MOTOR_SPEED, RADIUS_ROBOT, WHEEL_RADIUS, STEPS_PER_ROTATION, DISTANCE_PER_STEP

"""
    Send a command to the ESP32 to control motor movements.
"""
def send_command(stepsX, speedX, stepsY, speedY, stepsZ, speedZ):
    
    url = f"http://{esp32_ip}/control"
    params = {
        'stepsX': stepsX,
        'speedX': speedX,
        'stepsY': stepsY,
        'speedY': speedY,
        'stepsZ': stepsZ,
        'speedZ': speedZ
    }
    try:
        response = requests.get(url, params=params)
        print(response.text)
    except requests.RequestException as e:
        print(f"Error sending request: {e}")


"""
    Send a command to trigger the firing sequece of the selenoid.
"""
def send_strike_command(chargeDuration):
    url = f"http://{esp32_ip}/strike"
    params = {'chargeDuration': chargeDuration}
    response = requests.get(url, params=params)
    print(response.text)


# POLAR MOTION FUNCTIONS
    
"""
    Calculate the number of steps for rotation based on the given angle.
    """
def calculate_rotation_steps(angle):
    
    path_length = angle / 360 * 2 * math.pi * RADIUS_ROBOT
    rot_rot_num = path_length / (math.pi * 2 * WHEEL_RADIUS)
    return int(rot_rot_num * STEPS_PER_ROTATION)


"""
    Calculate the number of steps for translation based on the given distance.
"""
def calculate_translation_steps(distance):
    
    return int(distance / DISTANCE_PER_STEP * STEPS_PER_ROTATION)


# CARTESIAN MOTION FUNCTIONS

# TODO: @Ella, please add your functions for cartesian motion function here

