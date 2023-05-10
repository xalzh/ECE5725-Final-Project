from flask import Flask, render_template, Response
import cv2
import imutils
import time

app = Flask(__name__)

def gen_frames():  
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = imutils.resize(frame, width=400)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.02)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/index.html')  # Change this line
def index():
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RPi4 Camera Stream</title>
</head>
<body>
    <h1>Raspberry Pi 4 Camera Stream</h1>
    <img src="/video_feed" alt="Live Video Feed">
</body>
</html>
    '''
    return html_content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)