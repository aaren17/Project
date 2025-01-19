from flask import Flask, Response, jsonify
import cv2
import time

app = Flask(__name__)

# Replace camera with a video file (provide a valid video file path)
video_path = "D:\\Downloads\\istockphoto-1084342338-640_adpp_is.mp4"
camera = cv2.VideoCapture(video_path)

# Global variable to store detected anomalies
anomalies = []

# Function to detect motion anomalies
def detect_anomalies(frame, prev_frame):
    global anomalies
    if prev_frame is None:
        return frame

    # Compute the absolute difference between the current frame and the previous frame
    diff = cv2.absdiff(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                       cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY))
    # Apply a threshold to highlight significant differences (motion)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    # Count non-zero (changed) pixels
    non_zero_count = cv2.countNonZero(thresh)

    # If motion exceeds a threshold, log it as an anomaly
    if non_zero_count > 5000:  # Adjust this threshold based on your use case
        timestamp = time.strftime('%H:%M:%S')
        anomalies.append({"timestamp": timestamp, "description": "Motion detected"})
        anomalies = anomalies[-10:]  # Keep only the last 10 anomalies

    return frame

# Function to generate video frames
def generate_frames():
    prev_frame = None
    while True:
        success, frame = camera.read()
        if not success:
            # Restart the video if it ends
            camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Detect anomalies
        prev_frame = detect_anomalies(frame, prev_frame)

        # Draw the anomaly message on the frame
        for idx, anomaly in enumerate(anomalies[-3:]):  # Show the last 3 anomalies
            cv2.putText(frame, f"{anomaly['timestamp']}: {anomaly['description']}",
                        (10, 30 + idx * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Video stream route
@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Anomaly data route
@app.route('/anomalies', methods=['GET'])
def get_anomalies():
    return jsonify(anomalies)

# Main entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
