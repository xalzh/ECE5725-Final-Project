"""
5/11/2023 by Zehao Li

This Python module defines a multithreading camera class for real-time object tracking and video stabilization.
The 'Camera' class extends the 'Thread' class from the 'threading' library.

The main functionalities of the Camera class are:
- Initialize the camera and tracking settings.
- Continuously capture frames from the camera.
- Process frames based on the current operating mode (object tracking or stabilization).
- Update the screen with the processed frames.
- Listen for user input to stop the program.
- Provide methods to interact with the tracking settings (e.g., get, reset, stop, resume).

To achieve object tracking, it uses the MOSSE (Minimum Output Sum of Squared Error) tracker
from the 'object_tracking' module. The camera feed is processed frame-by-frame, and the
tracker follows the selected region of interest (ROI) throughout the video.

In the case of video stabilization, the class is designed to work with a stabilization algorithm
which is not explicitly defined within this module. The 'roll_error' is used in this context.

This module also uses the OpenCV library for video capture and image processing tasks,
and the 'threading' library for multithreading processing to ensure real-time performance.
"""
import threading
import cv2
from object_tracking import MOSSE
import time


class Camera(threading.Thread):
    """
    The Camera class is a subclass of Python's threading.Thread class. It represents a separate thread
    that handles the camera operations.

    It is initialized with a threading event, a video capture object, flags indicating whether object
    tracking (is_mode1) or stabilization (is_mode2) is active, and a screen object for displaying messages.

    The Camera class handles object tracking using the MeanShift Object Tracking System (MOSSE) and
    displays the camera feed in real-time.
    """
    def __init__(self, ready_event, cap, is_mode1, is_mode2, screen):
        super().__init__()
        self.latest_frame = None
        self.roi = None
        self.roi_lost = False
        self.selected_roi = False
        self.ready_event = ready_event
        self.mosse = MOSSE()
        self.screen = screen
        self.cap = cap
        self.is_mode1 = is_mode1
        self.is_mode2 = is_mode2
        self.stop_event = threading.Event()
        self.message = None
        self.roll_error = None
    
    def stop(self):
        # Sets a threading event to signal that the camera thread should stop.
        self.stop_event.set()
    
    def set_message(self, msg):
        # Updates the message to be displayed on the screen.
        self.message = msg
    
    def cancel(self):
        # Cancels the current tracking operation.
        self.roi = None
        self.roi_lost = False
        self.selected_roi = False
        self.mosse = MOSSE()

    def reset_tracking(self):
        # Resets the tracking operation by reinitializing the tracker.
        self.selected_roi = False
        self.mosse.selected_roi = False
        self.roi = None
        del self.mosse.tracker

    def resume_tracking(self, current_frame):
        # Resumes tracking by reinitializing the tracker with the initial region of interest (ROI).
        if self.mosse.initial_roi_frame is not None:
            self.mosse.tracker = cv2.legacy.TrackerMOSSE_create()
            bbox = (self.mosse.roi[0][0], self.mosse.roi[0][1],
                    abs(self.mosse.roi[1][0] - self.mosse.roi[0][0]),
                    abs(self.mosse.roi[1][1] - self.mosse.roi[0][1]))
            self.mosse.tracker.init(self.mosse.initial_roi_frame, bbox) # Use the original frame
            self.selected_roi = True
            self.mosse.selected_roi = True

    def get_roi_lost(self):
        # Returns the flag indicating whether the tracked object has been lost.
        return self.roi_lost

    def run(self):
        """
        Overrides threading.Thread's run method. This is the main loop of the camera thread.

        It continuously captures video frames from the camera, updates the object tracker, and
        sends the frames to the screen for display. It also handles user input for pausing,
        resuming, and canceling the tracking operation.
        """
        while not self.stop_event.is_set():
            # If we are not in stabilization mode, reset the roll error to None
            if not self.is_mode2:
                self.roll_error = None
            # If a message is set, send it to the screen and reset the message
            if self.message is not None:
                self.screen.show_message(self.message)
                self.message = None
            # If we are in object tracking mode (mode 1)
            if self.is_mode1 is True:
                # Read the current frame from the camera
                ret, frame = self.cap.read()
                self.latest_frame = frame
                # If frame reading fails, break the loop
                if not ret:
                    break
                # Apply MOSSE tracking to frame and get the updated frame, ROI, selected ROI and whether the ROI is lost
                frame, roi, selected_roi, roi_lost = self.mosse.run(frame)
                # Update the respective class variables
                self.roi_lost = roi_lost
                if selected_roi and self.mosse.initial_roi_frame is None:
                    self.mosse.save_initial_roi_frame(frame)
                self.roi = roi
                self.selected_roi = selected_roi
                self.screen.update_from_camera(frame, self.roll_error)
                # Quit if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                # If we are not in object tracking mode, still listen for 'q' to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                ret, frame = self.cap.read()
                # Update the screen with the current frame and potential roll error
                self.screen.update_from_camera(frame, self.roll_error)

            # Add a small sleep interval to reduce CPU usage
            time.sleep(0.02)

        # Set the ready event when the thread finishes executing
        self.ready_event.set() 

    def get_roi(self):
        # Returns the current region of interest and the flag indicating whether an object is being tracked.
        return self.roi, self.selected_roi