import pygame
from pygame.locals import *


# Define a UserInterface class
class UserInterface():
    # Initialize the UserInterface class with a pigpio.pi object and a video capture object
    def __init__(self, pi, cap):
        super().__init__()
        self.video_writer_initialized = None
        self.init_roll = None
        self.pin_vert = None
        self.pin_hori = None
        self.previous_heading = None
        pygame.init()
        self.touching = False
        self.pi = pi
        self.imu_data = None
        self.f = 50
        self.start_recording = False
        self.save_recording = False
        self.video_writer = None
        self.cap = cap
        self.init_heading = None
        self.init_pitch = None
        self.init_pitch = None

    # Define a function for manual control mode
    def mode1(self, pin_hori, pin_vert, shared_data):
        # Process Pygame events
        for event in pygame.event.get():
            if event.type is MOUSEBUTTONDOWN:
                self.touching = True
            elif event.type is MOUSEBUTTONUP:
                self.touching = False

        # If the mouse button is being held down or manual coordinates are available
        if self.touching is True or shared_data['manual_coor'] is not None:
            # Get mouse position and calculate the differences from the center of the screen
            pos = pygame.mouse.get_pos()
            x, y = pos
            dx = x - 160
            dy = y - 120
            # If manual coordinates are available, overwrite the values of x, y, dx, dy
            if shared_data['manual_coor'] is not None:
                x = shared_data['manual_coor']['x']
                y = shared_data['manual_coor']['y']
                dx = (x - 320) * 5
                dy = (y - 240) * 5
            # Get the current PWM duty cycles for the horizontal and vertical pins
            current_pwm_hori = self.pi.get_PWM_dutycycle(pin_hori)
            current_pwm_vert = self.pi.get_PWM_dutycycle(pin_vert)
            # Calculate new PWM duty cycles based on mouse position
            new_pwm_hori = current_pwm_hori - 10 * dx
            new_pwm_vert = current_pwm_vert + 10 * dy
            # Update the PWM duty cycles if they are within valid ranges
            if 36000 < new_pwm_hori < 115000:  # left max 115000, right max 36000
                self.pi.hardware_PWM(pin_hori, self.f, int(new_pwm_hori))
            if 35000 < new_pwm_vert < 105000:  # up max 105000, down max 35000
                self.pi.hardware_PWM(pin_vert, self.f, int(new_pwm_vert))

    # Define a function for automatic control mode based on image region of interest (ROI)
    def mode2(self, camera, pid_hori_mode2, pid_vert_mode2, pin_hori, pin_vert):
        # Get ROI from the camera
        roi, selected_roi = camera.get_roi()
        roi_lost = camera.get_roi_lost()
        # If the ROI is available and selected and not lost
        if roi is not None and len(roi) == 2 and selected_roi is True and not roi_lost:
            # Calculate the center of the ROI
            roi_center = [(roi[1][0] + roi[0][0]) / 2, (roi[1][1] + roi[0][1]) / 2]
            delta_time = 0.02
            # Calculate the difference between the center of the ROI and the center of the image
            delta = [roi_center[0] - 320, roi_center[1] - 240]
            # Update the PID controllers with the error and time difference
            control_signal_hori = pid_hori_mode2.update(delta[0], delta_time)
            control_signal_vert = pid_vert_mode2.update(delta[1], delta_time)
            # Get the current PWM duty cycles for the horizontal and vertical pins
            current_pwm_hori = self.pi.get_PWM_dutycycle(pin_hori)
            current_pwm_vert = self.pi.get_PWM_dutycycle(pin_vert)
            # Calculate new PWM duty cycles based on PID output
            new_pwm_hori = current_pwm_hori - control_signal_hori
            new_pwm_vert = current_pwm_vert + control_signal_vert
            # Update the PWM duty cycles if they are within valid ranges
            if 36000 < new_pwm_hori < 115000:  # left max 115000, right max 36000
                self.pi.hardware_PWM(pin_hori, self.f, int(new_pwm_hori))
            if 35000 < new_pwm_vert < 105000:  # up max 105000, down max 35000
                self.pi.hardware_PWM(pin_vert, self.f, int(new_pwm_vert))

    # Define a function for automatic control mode based on IMU data
    def mode3(self, camera, imu, pid_hori_mode3, pid_vert_mode3, pin_hori, pin_vert):
        # Read IMU data
        self.imu_data = imu.read_bno_data()
        self.pin_hori = pin_hori
        self.pin_vert = pin_vert
        # Get the heading, roll, and pitch from the IMU data
        heading, roll, pitch = self.imu_data['euler']

        if heading is not None and pitch is not None and roll is not None:
            # Calculate the errors in heading, pitch, and roll
            heading_error = (heading - self.init_heading + 180) % 360 - 180
            pitch_error = (pitch - self.init_pitch + 180) % 360 - 180
            roll_error = (roll - self.init_roll + 180) % 360 - 180
            camera.roll_error = roll_error
            interval_delta = (heading - self.previous_heading + 180) % 360 - 180
            if abs(interval_delta) >= 5:
                self.init_heading = heading
                heading_error = 0
            # Update the PID controllers with the errors
            pid_hori_output = pid_hori_mode3.update(heading_error, 0.02)
            pid_vert_output = pid_vert_mode3.update(pitch_error, 0.02)
            # Get the current PWM duty cycles for the horizontal and vertical pins
            current_pwm_hori = self.pi.get_PWM_dutycycle(pin_hori)
            current_pwm_vert = self.pi.get_PWM_dutycycle(pin_vert)
            # Calculate new PWM duty cycles based on PID output
            new_pwm_hori = current_pwm_hori + pid_hori_output
            new_pwm_vert = current_pwm_vert + pid_vert_output
            # Update the PWM duty cycles if they are within valid ranges
            if 36000 < new_pwm_hori < 115000:  # left max 115000, right max 36000
                self.pi.hardware_PWM(pin_hori, self.f, int(new_pwm_hori))
            if 35000 < new_pwm_vert < 105000:  # up max 105000, down max 35000
                self.pi.hardware_PWM(pin_vert, self.f, int(new_pwm_vert))
            # Update the previous heading
            self.previous_heading = heading

    '''def mode4(self):
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
                print("Failed to read frame")'''
