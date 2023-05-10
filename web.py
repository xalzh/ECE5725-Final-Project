from flask import Flask, render_template, Response, request
from multiprocessing import Queue, Manager
import RPi.GPIO as GPIO
import json
import time
from rolling_control import Rolling_Control 

app = Flask(__name__)
q = Queue()
mode = 1
shared_data = {'mode':1, 'button_22': False, 'button_23': False, 'button_27': False}

rolling = Rolling_Control()

def gen_frames():  
    global shared_data
    while True:
        if not q.empty():  # Check if the queue is not empty
            frame = q.get()  # Get the next frame from the queue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/index.html')  
def index():
    return render_template('index.html')

@app.route('/button_click', methods=['POST'])
def button_click():
    global shared_data
    button_id = request.json['button_id']
    print(f'Button "{button_id}" clicked')
    # set shared_data
    shared_data['button_id'] = button_id
    return 'Button click handled'

@app.route('/change_mode', methods=['POST'])
def change_mode():
    global mode
    mode = request.json['mode']
    print(f'Mode changed to {mode}')  # Handle the mode change in your main program
    return 'Mode change handled'

@app.route('/control_rolling', methods=['POST'])
def control_rolling():
    rolling_direction = request.json['rolling_direction']
    if rolling_direction == "forward":
        rolling.rolling_forward()
    elif rolling_direction == "backward":
        rolling.rolling_backward()
    elif rolling_direction == "right":
        rolling.rolling_right()
    elif rolling_direction == "left":
        rolling.rolling_left()
    print(f'Car is rolling {rolling_direction}')
    return 'Rolling control handled'

@app.route('/exit_rolling', methods=['POST'])
def exit_rolling():
    rolling.rolling_exit()
    print(f'Car stops rolling')
    return 'Rolling control handled'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
