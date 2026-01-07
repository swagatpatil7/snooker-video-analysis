import sys
import json
import cv2
import numpy as np
from collections import defaultdict

video_path = sys.argv[1]

# Open video
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(json.dumps({"status": "error", "message": "Cannot open video"}))
    sys.exit(1)

# Get video properties
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
duration = total_frames / fps if fps > 0 else 0

# ----- COLOR DETECTION LOGIC -----

# HSV color ranges for snooker balls
color_ranges = {
    'red': [
        (np.array([0, 100, 100]), np.array([10, 255, 255])),      # Lower red
        (np.array([160, 100, 100]), np.array([180, 255, 255]))    # Upper red
    ],
    'yellow': [
        (np.array([20, 100, 100]), np.array([30, 255, 255]))
    ],
    'green': [
        (np.array([40, 50, 50]), np.array([80, 255, 255]))
    ],
    'brown': [
        (np.array([10, 50, 50]), np.array([20, 200, 200]))
    ],
    'blue': [
        (np.array([100, 100, 100]), np.array([130, 255, 255]))
    ],
    'pink': [
        (np.array([140, 50, 50]), np.array([170, 255, 255]))
    ],
    'black': [
        (np.array([0, 0, 0]), np.array([180, 255, 50]))
    ],
    'white': [
        (np.array([0, 0, 200]), np.array([180, 30, 255]))
    ]
}

# Point values for each ball (snooker rules)
ball_points = {
    'red': 1,
    'yellow': 2,
    'green': 3,
    'brown': 4,
    'blue': 5,
    'pink': 6,
    'black': 7,
    'white': 0  # Cue ball
}

# Track ball detections across frames
ball_frequency = defaultdict(int)
ball_movement_events = []

# Sample every 30 frames (to avoid processing every frame)
sample_interval = 30
frame_count = 0

print(f"Processing {total_frames} frames...", file=sys.stderr)

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    # Process only sampled frames
    if frame_count % sample_interval == 0:
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv = cv2.GaussianBlur(hsv, (5, 5), 0)
        
        detected_in_frame = {}
        
        # Detect each color
        for color_name, ranges in color_ranges.items():
            
            # Create mask for this color
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            
            for lower, upper in ranges:
                temp_mask = cv2.inRange(hsv, lower, upper)
                mask = cv2.bitwise_or(mask, temp_mask)
            
            # Clean up mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find ball-like shapes
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            valid_balls = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter by size (adjust based on your video)
                if area > 100 and area < 5000:
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        
                        # Check if circular (balls are round)
                        if circularity > 0.6:
                            valid_balls += 1
            
            if valid_balls > 0:
                ball_frequency[color_name] += valid_balls
                detected_in_frame[color_name] = valid_balls
        
        # Track movement events
        if detected_in_frame:
            ball_movement_events.append({
                'frame': frame_count,
                'balls': list(detected_in_frame.keys())
            })
    
    frame_count += 1

cap.release()

# ----- SCORING LOGIC -----

player1_score = 0
player2_score = 0
max_break = 0
current_break = 0
fouls = 0

current_player = 1
total_shots = len(ball_movement_events)

# Calculate scores based on detected balls
for i, event in enumerate(ball_movement_events):
    balls_in_play = event['balls']
    
    # Determine points based on ball color
    if 'red' in balls_in_play:
        points = 1
    elif 'yellow' in balls_in_play:
        points = 2
    elif 'green' in balls_in_play:
        points = 3
    elif 'brown' in balls_in_play:
        points = 4
    elif 'blue' in balls_in_play:
        points = 5
    elif 'pink' in balls_in_play:
        points = 6
    elif 'black' in balls_in_play:
        points = 7
    else:
        # No scoring ball = foul or miss
        fouls += 1
        current_break = 0
        current_player = 2 if current_player == 1 else 1
        continue
    
    # Award points to current player
    if current_player == 1:
        player1_score += points
    else:
        player2_score += points
    
    # Track break
    current_break += points
    max_break = max(max_break, current_break)
    
    # Alternate players (simplified logic)
    if i % 3 == 0:
        current_player = 2 if current_player == 1 else 1
        current_break = 0

# Prepare ball statistics
ball_stats = {}
for color, freq in ball_frequency.items():
    ball_stats[color] = {
        'detected': freq,
        'points_value': ball_points[color]
    }

# Final result JSON
result = {
    "status": "success",
    "video": video_path,
    "total_frames": total_frames,
    "fps": fps,
    "duration": f"{duration:.2f}s",
    "ball_detection": ball_stats,
    "analysis": {
        "player1": {
            "score": player1_score,
            "name": "Player 1"
        },
        "player2": {
            "score": player2_score,
            "name": "Player 2"
        },
        "break": max_break,
        "fouls": fouls,
        "total_shots": total_shots
    },
    "message": "Video analyzed with OpenCV color detection"
}

print(json.dumps(result))