import cv2
import numpy as np

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
        # Assuming the largest contour is the white table
        largest_contour = max(contours, key=cv2.contourArea)
        return largest_contour
    return None

def detect_balls(frame, table_contour):
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define color range for detecting a black ball
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])
    black_mask = cv2.inRange(hsv, lower_black, upper_black)

    # Define color range for detecting a tennis ball (fluorescent yellow)
    lower_yellow = np.array([25, 50, 50])  # These values are just examples
    upper_yellow = np.array([35, 255, 255]) 
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Create a mask from the table contour
    table_mask = np.zeros_like(frame[:, :, 0])
    cv2.drawContours(table_mask, [table_contour], -1, 255, -1)

    # Detect balls within the table area
    detect_and_draw_balls(frame, black_mask, table_mask, (255, 255, 0)) # Black balls
    detect_and_draw_balls(frame, yellow_mask, table_mask, (255, 0, 255)) # Tennis balls

    # Draw the table contour
    cv2.drawContours(frame, [table_contour], -1, (0, 255, 255), 3) # Yellow contour

def detect_and_draw_balls(frame, color_mask, table_mask, color):
    # Combine the table mask with the color mask
    combined_mask = cv2.bitwise_and(color_mask, color_mask, mask=table_mask)

    # Find contours for the balls
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 100:  # Threshold area
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(frame, center, radius, color, 2)  # Draw circle around the ball

# Capture video from webcam or a video file
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect the white table area
    table_contour = detect_white_area(frame)

    if table_contour is not None:
        # Detect and draw balls within the white table area
        detect_balls(frame, table_contour)

    cv2.imshow('Detected Balls within White Table Area', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
