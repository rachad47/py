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
    return contours

def find_center(contour):
    M = cv2.moments(contour)
    if M['m00'] != 0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        return (cx, cy)
    return None


# Capture video from webcam or a video file
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus

while True:
    ret, frame = cap.read()
    if not ret:
        break

    table_contour = detect_white_area(frame)

    if table_contour is not None:
        table_mask = np.zeros_like(frame[:, :, 0])
        cv2.drawContours(table_mask, [table_contour], -1, 255, -1)
        pink_paper_box = detect_pink_paper(frame, table_mask)

        if pink_paper_box is not None:
            pink_paper_mask = np.zeros_like(frame[:, :, 0])
            cv2.drawContours(pink_paper_mask, [pink_paper_box], 0, 255, -1)

            # Define color ranges for blue and black
            lower_yellow = np.array([100, 160, 150])
            upper_yellow = np.array([140, 200, 180])
            lower_black = np.array([0, 0, 0])
            upper_black = np.array([100, 100, 100])
            lower_red = np.array([25, 25, 130])
            upper_red = np.array([75, 75, 180])

            # Detect blue and black spots
            blue_spots = detect_colored_spots(frame, (lower_yellow, upper_yellow), pink_paper_mask)
            black_spots = detect_colored_spots(frame, (lower_black, upper_black), pink_paper_mask)
            red_spots = detect_colored_spots(frame, (lower_red, upper_red), pink_paper_mask)

            
            if black_spots and red_spots and blue_spots:
                black_center = find_center(black_spots[0])
                red_center = find_center(red_spots[0])
                yellow_center = find_center(blue_spots[0])  # assuming blue_spots are actually yellow

                if black_center and red_center:
                    # Draw X-axis (Black to Red)
                    cv2.line(frame, black_center, red_center, (255, 0, 0), 2)
                    cv2.putText(frame, 'X-axis', red_center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                if black_center and yellow_center:
                    # Draw Y-axis (Black to Yellow)
                    cv2.line(frame, black_center, yellow_center, (0, 255, 0), 2)
                    cv2.putText(frame, 'Y-axis', yellow_center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


            # Draw contours color spots
            cv2.drawContours(frame, blue_spots, -1, (255, 0, 0), 1)  # yellow contours
            cv2.drawContours(frame, black_spots, -1, (0, 0, 255), 1)  # Black contours
            cv2.drawContours(frame, red_spots, -1, (0, 255, 255), 1) # Red contours

            # Draw a green rectangle around the pink paper
            cv2.drawContours(frame, [pink_paper_box], 0, (0, 255, 0), 2)

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
