import threading
import cv2
from object_tracking import MOSSE
import time


class Camera(threading.Thread):
    def __init__(self, ready_event, cap, is_mode2):
        super().__init__()
        self.roi = None
        self.roi_lost = False
        self.selected_roi = False
        self.ready_event = ready_event
        self.mosse = MOSSE()
        self.cap = cap
        self.is_mode2 = is_mode2
        self.stop_event = threading.Event()
    
    def stop(self):
        self.stop_event.set()
    
    def cancel(self):
        self.roi = None
        self.roi_lost = False
        self.selected_roi = False
        self.mosse = MOSSE()

    def reset_tracking(self):
        self.selected_roi = False
        self.mosse.selected_roi = False
        self.roi = None
        del self.mosse.tracker

    def resume_tracking(self, current_frame):
        if self.mosse.initial_roi_frame is not None:
            self.mosse.tracker = cv2.legacy.TrackerMOSSE_create()
            bbox = (self.mosse.roi[0][0], self.mosse.roi[0][1],
                    abs(self.mosse.roi[1][0] - self.mosse.roi[0][0]),
                    abs(self.mosse.roi[1][1] - self.mosse.roi[0][1]))
            self.mosse.tracker.init(self.mosse.initial_roi_frame, bbox) # Use the original frame
            self.selected_roi = True
            self.mosse.selected_roi = True

    def get_roi_lost(self):
        return self.roi_lost

    def run(self):
        while not self.stop_event.is_set():
            if self.is_mode2 is True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                frame, roi, selected_roi, roi_lost = self.mosse.run(frame)
                self.roi_lost = roi_lost
                if selected_roi and self.mosse.initial_roi_frame is None:
                    self.mosse.save_initial_roi_frame(frame)
                self.roi = roi
                self.selected_roi = selected_roi
                frame1 = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_NEAREST)
                frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGRA2BGR565)
                frame1 = frame1.tobytes()
                f = open("/dev/fb1", "wb")
                f.write(frame1)
                f.close()
                # cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                ret, frame = self.cap.read()
                frame1 = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_NEAREST)
                frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGRA2BGR565)
                frame1 = frame1.tobytes()
                f = open("/dev/fb1", "wb")
                f.write(frame1)
                f.close()

            # Add a small sleep interval to reduce CPU usage
            time.sleep(0.02)

        # Set the ready event when the thread finishes executing
        self.ready_event.set()

    # Add a method to get the current ROI value
    def get_roi(self):
        return self.roi, self.selected_roi