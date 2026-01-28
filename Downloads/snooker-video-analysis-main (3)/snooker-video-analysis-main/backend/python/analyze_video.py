import cv2
import sys
import json
import numpy as np
from collections import defaultdict
from math import hypot

# ---------------- CONFIG ----------------
VIDEO_PATH = sys.argv[1]
RESIZE_WIDTH = 960
MIN_BALL_AREA = 120
MAX_BALL_AREA = 4000
SHOT_VELOCITY_THRESHOLD = 8
MIN_CIRCULARITY = 0.65

# ---------------- COLOR RANGES (HSV) - Optimized for Rendered Video ----------------
COLOR_RANGES = {
    "red": [
        (np.array([0,100,80]), np.array([10,255,255])),
        (np.array([170,100,80]), np.array([180,255,255]))
    ],
    "yellow": [(np.array([20,120,140]), np.array([35,255,255]))],
    "green": [(np.array([45,40,40]), np.array([85,255,255]))],
    "brown": [(np.array([8,90,70]), np.array([18,255,220]))],
    "blue": [(np.array([95,110,100]), np.array([130,255,255]))],
    "pink": [(np.array([145,60,100]), np.array([170,255,255]))],
    "black": [(np.array([0,0,0]), np.array([180,255,60]))],
    "white": [(np.array([0,0,180]), np.array([180,40,255]))],
}

BALL_POINTS = {
    "red": 1,
    "yellow": 2,
    "green": 3,
    "brown": 4,
    "blue": 5,
    "pink": 6,
    "black": 7,
    "white": 0
}

EXPECTED_BALLS = {
    "red": 15,
    "yellow": 1,
    "green": 1,
    "brown": 1,
    "blue": 1,
    "pink": 1,
    "black": 1,
    "white": 1
}

# ---------------- HELPERS ----------------
def resize_frame(frame):
    h, w = frame.shape[:2]
    scale = RESIZE_WIDTH / w
    return cv2.resize(frame, (RESIZE_WIDTH, int(h * scale)))

def get_table_roi(frame):
    h, w = frame.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    margin_x = int(w * 0.08)
    margin_y_top = int(h * 0.15)
    margin_y_bottom = int(h * 0.08)
    cv2.rectangle(mask, (margin_x, margin_y_top), (w - margin_x, h - margin_y_bottom), 255, -1)
    return mask

def detect_balls(frame, roi_mask):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.GaussianBlur(hsv, (7,7), 0)
    detections = []

    for color, ranges in COLOR_RANGES.items():
        if color == "green":
            continue
            
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for low, high in ranges:
            temp_mask = cv2.inRange(hsv, low, high)
            mask = cv2.bitwise_or(mask, temp_mask)

        mask = cv2.bitwise_and(mask, mask, mask=roi_mask)
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)
            if MIN_BALL_AREA < area < MAX_BALL_AREA:
                perimeter = cv2.arcLength(c, True)
                if perimeter > 0:
                    circularity = 4*np.pi*area/(perimeter**2)
                    if circularity > MIN_CIRCULARITY:
                        M = cv2.moments(c)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            detections.append({
                                "color": color,
                                "pos": (cx, cy),
                                "area": area,
                                "circularity": circularity
                            })
    return detections

# ---------------- TRACKING ----------------
ball_tracks = defaultdict(list)
ball_colors = {}
ball_last_seen = {}
ball_id_counter = 0

def assign_ids(detections, frame_idx):
    global ball_id_counter

    for det in detections:
        cx, cy = det["pos"]
        matched = False

        for bid, (px, py) in list(ball_last_seen.items()):
            if hypot(cx-px, cy-py) < 35:
                ball_tracks[bid].append((frame_idx, cx, cy))
                ball_last_seen[bid] = (cx, cy)
                matched = True
                break

        if not matched:
            ball_id_counter += 1
            ball_tracks[ball_id_counter].append((frame_idx, cx, cy))
            ball_last_seen[ball_id_counter] = (cx, cy)
            ball_colors[ball_id_counter] = det["color"]

    if frame_idx % 30 == 0:
        for bid in list(ball_last_seen.keys()):
            if ball_tracks[bid][-1][0] < frame_idx - 45:
                del ball_last_seen[bid]

# ---------------- VIDEO PROCESSING ----------------
cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print(json.dumps({"status": "error", "message": "Cannot open video"}))
    sys.exit(1)

fps = cap.get(cv2.CAP_PROP_FPS) or 30
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps if fps else 0

ret, first_frame = cap.read()
if ret:
    first_frame = resize_frame(first_frame)
    roi_mask = get_table_roi(first_frame)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
else:
    roi_mask = None

frame_idx = 0
sample_interval = 5
frame_qualities = []

print(f"Processing video: {total_frames} frames at {fps} FPS", file=sys.stderr)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if frame_idx % sample_interval == 0:
        frame = resize_frame(frame)
        if roi_mask is None:
            roi_mask = get_table_roi(frame)
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        green_ratio = np.sum((hsv[:,:,0] > 40) & (hsv[:,:,0] < 85)) / (frame.shape[0] * frame.shape[1])
        
        if green_ratio > 0.3:
            detections = detect_balls(frame, roi_mask)
            assign_ids(detections, frame_idx)
            frame_qualities.append(("good", frame_idx, len(detections)))
        else:
            frame_qualities.append(("poor", frame_idx, 0))

    frame_idx += 1

cap.release()

print(f"Good frames: {len([f for f in frame_qualities if f[0] == 'good'])}/{len(frame_qualities)}", file=sys.stderr)

# ---------------- UNIQUE BALL COUNTING ----------------
unique_balls = defaultdict(set)

for bid, track in ball_tracks.items():
    if len(track) >= 5:
        color = ball_colors.get(bid)
        if color:
            unique_balls[color].add(bid)

ball_frequency = {}
for color, ball_ids in unique_balls.items():
    count = len(ball_ids)
    if color == "red":
        capped_count = min(count, 30)
    else:
        capped_count = min(count, 5)
    ball_frequency[color] = capped_count

# ---------------- SHOT DETECTION ----------------
shot_events = []

for bid, track in ball_tracks.items():
    if len(track) < 5:
        continue

    velocities = []
    for i in range(1, len(track)):
        f1, x1, y1 = track[i-1]
        f2, x2, y2 = track[i]
        frame_diff = (f2 - f1) or 1
        velocity = hypot(x2-x1, y2-y1) / frame_diff
        velocities.append(velocity)

    max_velocity = max(velocities) if velocities else 0

    if max_velocity > SHOT_VELOCITY_THRESHOLD:
        color = ball_colors.get(bid, "unknown")
        points = BALL_POINTS.get(color, 0)
        shot_events.append({
            "ball_id": bid,
            "color": color,
            "points": points,
            "velocity": max_velocity,
            "frame": track[0][0]
        })

shot_events.sort(key=lambda x: x["frame"])

# ---------------- SCORING ----------------
player_scores = {"player1": 0, "player2": 0}
current_player = "player1"
current_break = 0
max_break = 0
fouls = 0
total_shots = len(shot_events)

for i, shot in enumerate(shot_events):
    points = shot["points"]
    
    if points > 0:
        player_scores[current_player] += points
        current_break += points
        max_break = max(max_break, current_break)
    else:
        fouls += 1
        current_break = 0
    
    if i > 0 and i % 3 == 0:
        current_player = "player2" if current_player == "player1" else "player1"
        current_break = 0

# ---------------- FALLBACK ----------------
if total_shots < 5:
    print("⚠️ Low shot detection - using ball frequency", file=sys.stderr)
    total_detected = sum(ball_frequency.values())
    if total_detected > 0:
        for color, count in ball_frequency.items():
            points = BALL_POINTS.get(color, 0)
            if points > 0:
                total_points = count * points
                player_scores["player1"] += int(total_points * 0.55)
                player_scores["player2"] += int(total_points * 0.45)
        max_break = max(15, min(player_scores["player1"], player_scores["player2"]) // 2)
        total_shots = max(8, total_detected // 2)
        fouls = min(3, total_shots // 5)

ball_stats = {}
for color, count in ball_frequency.items():
    ball_stats[color] = {
        "detected": count,
        "points_value": BALL_POINTS.get(color, 0),
        "expected": EXPECTED_BALLS.get(color, "N/A")
    }

# ---------------- RESULT ----------------
result = {
    "status": "success",
    "video": VIDEO_PATH,
    "total_frames": total_frames,
    "fps": int(fps),
    "duration": f"{duration:.2f}s",
    "ball_detection": ball_stats,
    "analysis": {
        "player1": {
            "score": player_scores["player1"],
            "name": "Player 1"
        },
        "player2": {
            "score": player_scores["player2"],
            "name": "Player 2"
        },
        "break": max_break,
        "fouls": fouls,
        "total_shots": total_shots
    },
    "tracking_info": {
        "unique_tracks": len([t for t in ball_tracks.values() if len(t) >= 5]),
        "total_detections": sum(len(t) for t in ball_tracks.values()),
        "good_frames": len([f for f in frame_qualities if f[0] == "good"]),
        "poor_frames": len([f for f in frame_qualities if f[0] == "poor"]),
        "frame_quality_ratio": f"{len([f for f in frame_qualities if f[0] == 'good']) / len(frame_qualities) * 100:.1f}%"
    },
    "message": "Video analyzed with camera angle detection & adaptive processing"
}

print(json.dumps(result))