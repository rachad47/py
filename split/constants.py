import numpy as np

esp32_ip = "192.168.137.244"
MOTOR_SPEED = 2200
RADIUS_ROBOT = 15.242 / 100
WHEEL_RADIUS = 0.03
STEPS_PER_ROTATION = 1600
DISTANCE_PER_STEP = 0.214
POOL_BALL_DIAMETER=5.7

# Define constants for HSV values
LOWER_CENTER = np.array([0, 0, 0])
UPPER_CENTER = np.array([179, 100, 120])

LOWER_Y_AXIS = np.array([2, 100, 100])
UPPER_Y_AXIS = np.array([12, 180, 200])

LOWER_BALL = np.array([30, 115, 110])
UPPER_BALL = np.array([35, 130, 160])