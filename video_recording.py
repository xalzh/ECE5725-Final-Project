import cv2
import threading
import datetime
import time


class Recording(threading.Thread):
    def __init__(self, ready_event, cap):
        super().__init__()
        self.ready_event = ready_event
        self.stop_event = threading.Event()
        self.start_recording = False
        self.save_recording = False
        self.video_writer = None
        self.cap = cap
    
    def stop(self):
        self.stop_event.set()
    
    def run(self):
        while  not self.stop_event.is_set():
            if self.start_recording and self.video_writer is None:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                video_file_name = f'output_{current_time}.avi'
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.video_writer = cv2.VideoWriter(video_file_name, fourcc, 20.0, (320, 240))
                self.video_writer_initialized = True
            
            if self.save_recording and self.video_writer is not None:
                print("save file...")
                self.video_writer.release()
                self.video_writer = None
                self.video_writer_initialized = False
                self.start_recording = False
                self.save_recording = False
            
            if self.start_recording:
                ret, frame = self.cap.read()
                if ret:
                    self.video_writer.write(frame)
                else:
                    print("Failed to read frame")
            