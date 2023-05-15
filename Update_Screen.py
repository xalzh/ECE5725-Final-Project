"""
5/11/2023 by Zehao Li

This script defines the Screen class for a Pygame-based graphical user interface. The main function of this class is
to display video feed from a camera and overlay it with text messages. The display is set up to work specifically on
a Raspberry Pi device with a PiTFT touchscreen. The video feed can be processed for errors and adjusted for display
requirements. The class also handles user interactions with the touchscreen.
"""
import cv2
import pygame
import numpy as np
import time
import os


# Defining a Screen class for video feed display and user interface operations
class Screen():
    def __init__(self):
        super()
        self.font = None
        self.lcd = None
        self.init_pygame()
        self.message = None
        self.message_start_time = None
        self.frame = None
        self.surface = None

    # Initialize Pygame with necessary settings
    def init_pygame(self):
        # Setting up the video driver and mouse driver
        os.environ["SDL_VIDEODRIVER"] = "fbcon"
        os.putenv('SDL_FBDEV', '/dev/fb0')  #
        os.putenv('SDL_MOUSEDRV', 'TSLIB')  # Track mouse clicks on piTFT
        os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
        pygame.init()
        # Setting up the display
        self.lcd = pygame.display.set_mode((320, 240))
        pygame.mouse.set_visible(False)
        self.font = pygame.font.Font(None, 30)  # Choose font size and type

    # Method to process a frame for display
    def get_processed_frame(self):
        frame = self.frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        return frame

    # Method to update the displayed frame from the camera feed
    def update_from_camera(self, frame, roll_error=None):
        # Checking if a valid frame was provided
        if frame is not None and not frame.size == 0:
            # Checking if a roll error was provided
            if roll_error is not None:
                # Rotate the image with the degrees of roll error to balance the video frame
                rotation_matrix = cv2.getRotationMatrix2D((320, 240), -roll_error, 1)
                rotated_frame = cv2.warpAffine(frame, rotation_matrix, (640, 480))
                cropped_frame = rotated_frame[120:380, 100:500]
                self.frame = cropped_frame
                frame = cv2.resize(cropped_frame, (320, 240), interpolation=cv2.INTER_NEAREST)
                # Convert the color format from BGR to RGB for display with Pygame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB format for Pygame
            else:
                # Resizing and converting the color format of the frame if no roll error was provided
                self.frame = frame
                frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_NEAREST)
                # Convert the color format from BGR to RGB for display with Pygame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB format for Pygame

            # Rotating and flipping the frame for correct orientation
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            # Creating a Pygame surface from the frame
            surface = pygame.surfarray.make_surface(frame)
            # Convert the frame surface to the same format as the destination surface (self.lcd)
            surface = surface.convert(self.lcd)
            # Displaying the frame on the screen
            self.lcd.blit(surface, (0, 0))
            self.surface = surface

            # Displaying a message on the screen for 2 seconds
            if self.message and self.message_start_time:
                if time.time() - self.message_start_time < 2:
                    text_surface = self.font.render(self.message, True, (255, 255, 255))
                    text_width, text_height = text_surface.get_size()
                    text_position = (160 - text_width // 2, 120 - text_height // 2)
                    self.lcd.blit(text_surface, text_position)  # Position the message on the screen
                else:
                    self.message = None
                    self.message_start_time = None
            # Update the Pygame display
            pygame.display.update()
        else:
            # If no frame was provided, keep displaying the last frame
            if self.surface is not None:
                self.lcd.blit(self.surface, (0, 0))
                pygame.display.update()

    # Method to set a message to be displayed on the screen
    def show_message(self, message):
        self.message = message
        self.message_start_time = time.time()
