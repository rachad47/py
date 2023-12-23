import cv2
import numpy as np
import math



def detect_backgroud_boudary(frame):
    # Convert to HSV for better color segmentation
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Define range for white color
    lower_white = np.array([0, 0, 100])
    upper_white = np.array([172, 120, 255])
    # Create a mask for white color
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    # Apply morphology to clean up the mask
    kernel = np.ones((5, 5), np.uint8)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)
    # Find contours for the white area
    contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(frame, [largest_contour], -1, (0, 255, 255), 3) # Yellow contour
        return largest_contour
    return None

def detect_pink_paper(frame, white_mask):
     # Convert to HSV for better color segmentation
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Define range for pink color
    lower_pink = np.array([145, 30, 30])
    upper_pink = np.array([250, 255, 255])

    # Create a mask for pink color
    pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
    # Apply the white area mask to the pink mask
    masked_pink = cv2.bitwise_and(pink_mask, pink_mask, mask=white_mask)

    # Find contours of the pink paper
    contours, _ = cv2.findContours(masked_pink, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Optional: Approximate the contour to simplify the shape
        epsilon = 0.01 * cv2.arcLength(largest_contour, True)
        approx_contour = cv2.approxPolyDP(largest_contour, epsilon, True)

        return approx_contour
    return None

def detect_colored_spots(frame, color_mask, region_mask):
    # Create a mask for colored spots
    colored_spots_mask = cv2.inRange(frame, color_mask[0], color_mask[1])
    # Apply the region mask to the colored spots mask
    masked_colored_spots = cv2.bitwise_and(colored_spots_mask, colored_spots_mask, mask=region_mask)
    # Find contours of the colored spots
    contours, _ = cv2.findContours(masked_colored_spots, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, -1, (255, 255, 255), 1)
    return contours

def calculate_center(contour):
    M = cv2.moments(contour)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return (cx, cy)
    return None

def draw_axes(frame, origin, y_point, label_offset=10):
    # Draw Y-axis as an arrow pointing to the yellow spot
    cv2.arrowedLine(frame, origin, y_point, (0, 255, 0), 2, tipLength=0.2)
    cv2.putText(frame, 'Y', (y_point[0] + label_offset, y_point[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    # Calculate the length of the Y-axis
    y_length = np.sqrt((y_point[0] - origin[0])**2 + (y_point[1] - origin[1])**2)

    # Calculate a perpendicular direction for the X-axis
    y_direction = (y_point[0] - origin[0], y_point[1] - origin[1])
    x_direction = (-y_direction[1], y_direction[0])

    # Normalize and scale the X direction to match the Y-axis length
    norm = np.sqrt(x_direction[0]**2 + x_direction[1]**2)
    x_direction = (int(x_direction[0]/norm * y_length), int(x_direction[1]/norm * y_length))

    # Define the end point for the X-axis
    x_point = (origin[0] + x_direction[0], origin[1] + x_direction[1])

    # Draw X-axis as an arrow of the same length as the Y-axis
    cv2.arrowedLine(frame, origin, x_point, (255, 0, 0), 2, tipLength=0.2)
    cv2.putText(frame, 'X', (x_point[0] - label_offset, x_point[1] +10 + label_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

def detect_balls(frame, table_contour, color_range, min_contour_area=100):
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the ball color
    ball_mask = cv2.inRange(hsv, color_range[0], color_range[1])

    # Create a mask from the table contour
    table_mask = np.zeros_like(frame[:, :, 0])
    cv2.drawContours(table_mask, [table_contour], -1, 255, -1)

    # Combine the table mask with the color mask
    combined_mask = cv2.bitwise_and(ball_mask, ball_mask, mask=table_mask)

    # Find contours for the balls
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    balls = []
    for contour in contours:
        if cv2.contourArea(contour) > min_contour_area:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            balls.append(((int(x), int(y)), int(radius)))
    
    return balls

def calculate_ball_measurements(frame, balls, origin, y_direction, ball_diameter_cm=7.0):
    ball_data = []
    y_length = math.sqrt(y_direction[0]**2 + y_direction[1]**2)

    for center, radius in balls:
        # Draw circle around the ball
        cv2.circle(frame, center, radius, (255, 255, 0), 2)
        cv2.line(frame, origin, center, (255, 100, 255), 2)  # Line from origin to ball

        # Calculate distance
        ball_vector = (center[0] - origin[0], center[1] - origin[1])
        distance_pixels = math.sqrt(ball_vector[0]**2 + ball_vector[1]**2)
        pixel_to_cm_ratio = ball_diameter_cm / (2 * radius)
        distance_cm = distance_pixels * pixel_to_cm_ratio

        # Calculate angle
        dot_product = ball_vector[0]*y_direction[0] + ball_vector[1]*y_direction[1]
        angle = math.acos(dot_product / (distance_pixels * y_length))
        angle_degrees = math.degrees(angle)

        # Determine the sign of the angle using the cross product
        cross_product_z = y_direction[0] * ball_vector[1] - y_direction[1] * ball_vector[0]
        angle_degrees = -angle_degrees if cross_product_z < 0 else angle_degrees

        # Store the calculated data
        ball_data.append((center, radius, distance_cm, angle_degrees))

    return ball_data
              
def detect_center_of_axis(frame, pink_paper_mask):
    # Convert the frame to HSV color space for better color segmentation
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define range for black color
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])

    # Create a mask for black color
    black_mask = cv2.inRange(hsv, lower_black, upper_black)

    # Apply the pink paper mask to the black mask
    masked_black = cv2.bitwise_and(black_mask, black_mask, mask=pink_paper_mask)

    # Find contours of the black spot
    contours, _ = cv2.findContours(masked_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Find the largest contour which will be the black spot
        largest_contour = max(contours, key=cv2.contourArea)
        return calculate_center(largest_contour)
    return None


# Capture video from webcam or a video file
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus

while True:
    ret, frameOrigin = cap.read()
    if not ret:
        break
    
    # Blur the frame to reduce noise
    frame = cv2.GaussianBlur(frameOrigin, (3,3), 0)
    table_contour = detect_backgroud_boudary(frame)

    if table_contour is not None:
        table_mask = np.zeros_like(frame[:, :, 0])
        cv2.drawContours(table_mask, [table_contour], -1, 255, -1)
        pink_paper_box = detect_pink_paper(frame, table_mask)

        origin = None  # Initialize the origin

        if pink_paper_box is not None:
            pink_paper_mask = np.zeros_like(frame[:, :, 0])
            cv2.drawContours(pink_paper_mask, [pink_paper_box], 0, 255, -1)  # note that here we are drawing the box on the mask
            cv2.drawContours(frame, [pink_paper_box], 0, (100, 50, 100), 2)  # while here we are drawing the box on the frame

            # Detect the black spot as the origin of our coordinate system
            lower_black = np.array([0, 0, 0])
            upper_black = np.array([180, 255, 50])
            black_spot=detect_colored_spots(frame, (lower_black, upper_black), pink_paper_mask)
            if black_spot:
                origin = calculate_center(black_spot[0])
                cv2.circle(frame, origin, 5, (0, 0, 255), -1)

            # Detect the yellow spot so that from the center to the yellow spot is the Y-axis
            lower_yellow = np.array([100, 150, 140])
            upper_yellow = np.array([150, 220, 220])            
            yellow_spots = detect_colored_spots(frame, (lower_yellow, upper_yellow), pink_paper_mask)
            y_direction = None
            yellow_center = None
            for spot in yellow_spots:
                yellow_center = calculate_center(spot)
                if yellow_center and origin:
                    y_direction = (yellow_center[0] - origin[0], yellow_center[1] - origin[1])
                    break

            if origin is not None and yellow_center is not None:
                draw_axes(frame, origin, yellow_center)

        # Detect balls
        if origin is not None and y_direction is not None:
            lower_black = np.array([0, 0, 0])
            upper_black = np.array([150, 150, 50])
            balls = detect_balls(frame, table_contour, (lower_black, upper_black))
            ball_measurements = calculate_ball_measurements(frame, balls, origin, y_direction)

            # Drawing and annotations
            for center, radius, distance_cm, angle_degrees in ball_measurements:
                midpoint = ((origin[0] + center[0]) // 2, (origin[1] + center[1]) // 2)
                cv2.putText(frame, f"{distance_cm:.1f} cm", midpoint, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 100), 2)
                cv2.putText(frame, f"{angle_degrees:.1f} degrees", (center[0] - 40, center[1] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 255), 2)

    cv2.imshow('Frame', frame)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord('p'):
        # Save the current measuraments to print later when 's' is pressed
        cv2.imshow('screenshot', frame)
        hold_measurement = ball_measurements
        
    elif key & 0xFF == ord('s'):
        if 'hold_measurement' in locals():
            for center, radius, distance, angle in hold_measurement:
                print(f"Ball at {center}: Distance = {distance:.1f} cm, Angle = {angle:.1f} degrees")

cap.release()
cv2.destroyAllWindows()
