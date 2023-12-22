import cv2
import numpy as np

def create_mask(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel), cv2.MORPH_OPEN, kernel)

def find_largest_contour(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return max(contours, key=cv2.contourArea) if contours else None

def detect_colors_with_masks(frame,lower_color, upper_color, boundary_mask):
    pink_mask = create_mask(frame, lower_color, upper_color)
    masked_pink = cv2.bitwise_and(pink_mask, pink_mask, mask= boundary_mask)
    return find_largest_contour(masked_pink)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    white_mask = create_mask(frame, np.array([0, 0, 100]), np.array([172, 120, 255]))
    table_contour = find_largest_contour(white_mask)

    if table_contour is not None:
        table_mask = np.zeros_like(frame[:, :, 0])
        cv2.drawContours(table_mask, [table_contour], -1, 255, -1)
        pink_paper_contour = detect_colors_with_masks(frame,  np.array([145, 30, 30]), np.array([250, 255, 255]) ,table_mask)

        if pink_paper_contour is not None:
            # Draw the exact contour of the pink paper
            cv2.drawContours(frame, [pink_paper_contour], 0, (0, 255, 0), 2)

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()










import cv2
import numpy as np

def create_mask(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel), cv2.MORPH_OPEN, kernel)

def find_largest_contour(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return max(contours, key=cv2.contourArea) if contours else None

def detect_colors_with_masks(frame,lower_color, upper_color, boundary_mask):
    pink_mask = create_mask(frame, lower_color, upper_color)
    masked_pink = cv2.bitwise_and(pink_mask, pink_mask, mask= boundary_mask)
    return find_largest_contour(masked_pink)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    white_mask = create_mask(frame, np.array([0, 0, 100]), np.array([172, 120, 255]))
    table_contour = find_largest_contour(white_mask)

    pink_mask = create_mask(frame, np.array([145, 30, 30]), np.array([250, 255, 255]))
    pink_paper_contour = find_largest_contour(pink_mask)

    black_mask = create_mask(frame, np.array([0, 0, 0]), np.array([150, 150, 50]))
    black_ball_contour = find_largest_contour(black_mask)


    if table_contour is not None:
        table_mask = np.zeros_like(frame[:, :, 0])
        cv2.drawContours(table_mask, [table_contour], -1, 255, -1)
        pink_paper_contour = detect_colors_with_masks(frame,  np.array([145, 30, 30]), np.array([250, 255, 255]) ,table_mask)
            # Draw the exact contour of the pink paper
        cv2.drawContours(frame, [pink_paper_contour], 0, (0, 255, 0), 2)

        paper_mask= np.zeros_like(frame[:, :, 0])
        if pink_paper_contour is not None:
            cv2.drawContours(paper_mask, [pink_paper_contour], -1, 255, -1)
        black_ball_contour = detect_colors_with_masks(frame, np.array([0, 0, 0]), np.array([150, 150, 50]), paper_mask)

        if black_ball_contour is not None:
            cv2.drawContours(frame, [black_ball_contour], 0, (0, 255, 0), 2)


    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
