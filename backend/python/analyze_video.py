import sys
import json
import cv2

video_path = sys.argv[1]

# Open video (just to confirm it exists)
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(json.dumps({"status": "error", "message": "Cannot open video"}))
    sys.exit(1)

# Dummy result for now
result = {
    "status": "success",
    "video": video_path,
    "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
    "message": "Video processed successfully"
}

cap.release()

print(json.dumps(result))