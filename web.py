from flask import Flask, render_template, Response, request
from multiprocessing import Queue, Manager
import RPi.GPIO as GPIO
import json
import time
from rolling_control import Rolling_Control 

app = Flask(__name__)
q = Queue()
mode = 1

rolling = Rolling_Control()

def gen_frames():  
    while True:
        if not q.empty():  # Check if the queue is not empty
            frame = q.get()  # Get the next frame from the queue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.02)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/index.html')  
def index():
    return render_template('index.html')

@app.route('/button_click', methods=['POST'])
def button_click():
    global shared_data, lock
    with lock:
        button_id = request.json['button_id']
        print(f'Button "{button_id}" clicked')
        if button_id == 'cancel-tracking':
            shared_data['coordinates'] = [None, None]
            shared_data['tracking_initialized'] = False  # reset the flag
        elif button_id == 'pause-tracking':
            shared_data['tracking_paused'] = True  # pause the tracking
        elif button_id == 'resume-tracking':
            shared_data['tracking_paused'] = False  # resume the tracking
        shared_data['functional'] = button_id
        return 'Button click handled'

@app.route('/change_mode', methods=['POST'])
def change_mode():
    global mode, shared_data, lock
    with lock:
        max_mode_num = 3
        if shared_data['mode_idx'] + 1 >= max_mode_num:
            shared_data['mode_idx'] = 0
        else:
            shared_data['mode_idx'] += 1
        shared_data['mode_change_signal'] = True

        mode = request.json['mode']
        if mode == 2 and shared_data['23']:
            shared_data['coordinates'] = [None, None]

        print(f'Mode changed to {mode}')
        return 'Mode change handled'

@app.route('/get_current_mode')
def get_current_mode():
    global shared_data, mode, lock
    with lock:
        mode = shared_data['mode_idx'] + 1
        if shared_data.get('tracking_status'):
            tracking_status = shared_data['tracking_status']
        else:
            tracking_status = False
        button22 = shared_data['22']
        button23 = shared_data['23']
        button27 = shared_data['27']
        shared_data['22'] = False
        shared_data['23'] = False
        shared_data['27'] = False
        return json.dumps({
            'mode': shared_data['mode_idx']+1, 
            'tracking_status': tracking_status,
            'button22': button22,
            'button23': button23,
            'button27': button27
            })
       
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

@app.route('/set_coordinates', methods=['POST'])
def set_coordinates():
    global shared_data, lock
    with lock:
        coordinates = request.json['coordinates']
        print(f'Coordinates received: {coordinates}')
        shared_data['coordinates'] = coordinates
        shared_data['tracking_initialized'] = False  # reset the flag
        return 'Coordinates set'

@app.route('/set_manual_coordinates', methods=['POST'])
def set_manual_coordinates():
    global shared_data, lock
    with lock:
        coordinates = request.json['coordinates']
        print(f'Manual coordinates received: {coordinates}')
        shared_data['manual_coor'] = coordinates
        return 'Manual coordinates set'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
