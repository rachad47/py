import cv2
import numpy as np
import math


def detect_white_area(frame):
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
        # Find the minimum area rectangle for the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(largest_contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        return box
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
    cv2.putText(frame, 'Y', (y_point[0] + label_offset, y_point[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

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
    cv2.putText(frame, 'X', (x_point[0] - label_offset, x_point[1] + label_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

def detect_balls(frame, table_contour, origin):
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define color range for detecting a black ball
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])
    black_mask = cv2.inRange(hsv, lower_black, upper_black)

    # Create a mask from the table contour
    table_mask = np.zeros_like(frame[:, :, 0])
    cv2.drawContours(table_mask, [table_contour], -1, 255, -1)

    # Detect balls within the table area and draw a line from the origin
    detect_and_draw_balls(frame, black_mask, table_mask, (255, 255, 0), origin)

    # Draw the table contour
    cv2.drawContours(frame, [table_contour], -1, (0, 255, 255), 3) # Yellow contour
     # Call detect_and_draw_balls with ball diameter
    detect_and_draw_balls(frame, black_mask, table_mask, (255, 255, 0), origin, 7.0)

def detect_and_draw_balls(frame, color_mask, table_mask, color, origin, ball_diameter_cm=7.0):
    # Combine the table mask with the color mask
    combined_mask = cv2.bitwise_and(color_mask, color_mask, mask=table_mask)

    # Find contours for the balls
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 100:  # Threshold area
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)

            # Draw circle around the ball
            cv2.circle(frame, center, radius, color, 2)

            # Draw line from the origin (center of pink paper) to the ball center
            if origin is not None:
                cv2.line(frame, origin, center, (255, 100, 255), 2)  # Line color: Blue

            # Calculate and display the distance
            distance_pixels = math.sqrt((center[0] - origin[0])**2 + (center[1] - origin[1])**2)
            pixel_to_cm_ratio = ball_diameter_cm / (2 * radius)
            distance_cm = distance_pixels * pixel_to_cm_ratio
            
            midpoint = ((origin[0] + center[0]) // 2, (origin[1] + center[1]) // 2)


            cv2.putText(frame, f"{distance_cm:.2f} cm", midpoint, 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 255), 2)

# Capture video from webcam or a video file
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus

while True:
    ret, frameOrigin = cap.read()
    if not ret:
        break
    
    frame = cv2.GaussianBlur(frameOrigin, (1, 1), 0)
    table_contour = detect_white_area(frame)

    if table_contour is not None:
        # Prepare mask for pink paper detection
        table_mask = np.zeros_like(frame[:, :, 0])
        cv2.drawContours(table_mask, [table_contour], -1, 255, -1)
        pink_paper_box = detect_pink_paper(frame, table_mask)

        pink_paper_center = None

        if pink_paper_box is not None:
            pink_paper_center = calculate_center(pink_paper_box)
            pink_paper_mask = np.zeros_like(frame[:, :, 0])
            cv2.drawContours(pink_paper_mask, [pink_paper_box], 0, 255, -1)
            pink_paper_center = calculate_center(pink_paper_box)

            # Mark the center of the pink paper with a red point
            if pink_paper_center:
                detect_balls(frame, table_contour, pink_paper_center)
                cv2.circle(frame, pink_paper_center, 5, (0, 0, 255), -1)

            lower_yellow = np.array([100, 160, 150])
            upper_yellow = np.array([140, 200, 180])

            yellow_spots = detect_colored_spots(frame, (lower_yellow, upper_yellow), pink_paper_mask)

            for spot in yellow_spots:
                yellow_center = calculate_center(spot)
                # Assuming the first detected yellow spot as the Y-axis point
                if yellow_spots:
                    yellow_center = calculate_center(yellow_spots[0])
                    if yellow_center:
                        draw_axes(frame, pink_paper_center, yellow_center)

        if pink_paper_center is not None:
            detect_balls(frame, table_contour, pink_paper_center)

            # Draw a green rectangle around the pink paper
            # cv2.drawContours(frame, [pink_paper_box], 0, (0, 255, 0), 2)
    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
