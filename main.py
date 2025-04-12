import cv2
import numpy as np
import time
from hand_tracking import HandDetector
from utils import count_fingers, get_color


cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector()
canvas = np.zeros((720, 1280, 3), dtype=np.uint8)

prev_x, prev_y = 0, 0
draw_color = (0, 0, 255)
brush_thickness = 7
eraser_thickness = 50
is_eraser_mode = False


toolbar_height = 100
toolbar = np.zeros((toolbar_height, 1280, 3), dtype=np.uint8)


colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0)]
color_buttons = [(i * 100 + 10, 10, (i + 1) * 100 - 10, 90) for i in range(len(colors))]

# Futuristic glow effect
def add_glow_effect(frame, x_min, y_min, x_max, y_max, color):
    overlay = frame.copy()
    cv2.rectangle(overlay, (x_min - 5, y_min - 5), (x_max + 5, y_max + 5), color, -1)
    alpha = 0.3  # Transparency factor
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)

    # Detect hands and positions
    frame = detector.findHands(frame)
    lm_list = detector.findPosition(frame, draw=True)

    fingers_up = 0  # Initialize with a default value

    if lm_list:
        fingers_up = count_fingers(lm_list)
        x1, y1 = lm_list[8][1], lm_list[8][2]  # Index fingertip
        x2, y2 = lm_list[12][1], lm_list[12][2]  # Middle fingertip

        # Check if the fingertip is in the toolbar area
        if y1 < toolbar_height:
            for i, (x_min, y_min, x_max, y_max) in enumerate(color_buttons):
                if x_min < x1 < x_max and y_min < y1 < y_max:
                    draw_color = colors[i]
                    is_eraser_mode = False  # Switch to drawing mode
                    break

        # Eraser mode (1 finger touching)
        if fingers_up == 1:
            is_eraser_mode = True

        # Drawing mode (2 fingers up)
        if fingers_up == 2:
            is_eraser_mode = False
            thickness = brush_thickness
            if prev_x == 0 and prev_y == 0:
                prev_x, prev_y = x1, y1
            cv2.line(canvas, (prev_x, prev_y), (x1, y1), draw_color, thickness)
            prev_x, prev_y = x1, y1
        elif is_eraser_mode and fingers_up == 1:
            # Erase only when touching
            cv2.circle(canvas, (x1, y1), eraser_thickness, (0, 0, 0), -1)
        else:
            prev_x, prev_y = 0, 0

    # Combine canvas and live video
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, inv_canvas = cv2.threshold(gray_canvas, 50, 255, cv2.THRESH_BINARY_INV)
    inv_canvas = cv2.cvtColor(inv_canvas, cv2.COLOR_GRAY2BGR)
    frame = cv2.bitwise_and(frame, inv_canvas)
    frame = cv2.bitwise_or(frame, canvas)

    # Draw toolbar with glow effect
    toolbar[:] = (50, 50, 50)
    for i, (x_min, y_min, x_max, y_max) in enumerate(color_buttons):
        add_glow_effect(toolbar, x_min, y_min, x_max, y_max, colors[i])
        cv2.rectangle(toolbar, (x_min, y_min), (x_max, y_max), colors[i], -1)
        if draw_color == colors[i] and not is_eraser_mode:
            cv2.rectangle(toolbar, (x_min, y_min), (x_max, y_max), (255, 255, 255), 3)

    # Add eraser button glow effect
    if is_eraser_mode:
        cv2.putText(toolbar, "Eraser", (1100, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Add toolbar to the frame
    frame[:toolbar_height, :] = toolbar

    # Add "Made by Mangal Bhadouriya" text on the side
    cv2.putText(frame, "Made by Mangal Bhadouriya", (10, 700), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Show color preview and feedback
    cv2.putText(frame, f"{fingers_up} fingers", (10, toolbar_height + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)

    cv2.imshow("Air Graffiti Wall", frame)

    key = cv2.waitKey(1)
    if key == ord('s'):
        timestamp = int(time.time())
        cv2.imwrite(f'drawings/drawing_{timestamp}.png', canvas)
        print("🎨 Drawing saved!")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


