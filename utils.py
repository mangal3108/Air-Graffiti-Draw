# utils.py

# Finger tip landmark IDs from Mediapipe
TIP_IDS = [4, 8, 12, 16, 20]

# Color map based on number of fingers up
COLOR_MAP = {
    1: (0, 0, 255),     # Red
    2: (0, 255, 0),     # Green
    3: (255, 0, 0),     # Blue
    4: (0, 255, 255),   # Yellow
    5: (255, 255, 255)  # White (eraser)
}

def count_fingers(lm_list):
    fingers = []
    if not lm_list or len(lm_list) < 21:
        return 0

    # Thumb
    fingers.append(1 if lm_list[TIP_IDS[0]][1] < lm_list[TIP_IDS[0] - 1][1] else 0)
    
    # 4 fingers
    for id in range(1, 5):
        fingers.append(1 if lm_list[TIP_IDS[id]][2] < lm_list[TIP_IDS[id] - 2][2] else 0)

    return sum(fingers)

def get_color(finger_count):
    return COLOR_MAP.get(finger_count, (0, 0, 255))
