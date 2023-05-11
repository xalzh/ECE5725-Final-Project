import cv2
import pygame
import numpy as np
import time
import signal
import os


class Screen():
    def __init__(self):
        super()
        self.lcd = None
        self.font = None
        self.init_pygame()
        self.message = None
        self.message_start_time = None
        self.frame = None
        self.surface = None

    def init_pygame(self):
        os.environ["SDL_VIDEODRIVER"] = "fbcon"
        os.putenv('SDL_FBDEV', '/dev/fb0')  #
        os.putenv('SDL_MOUSEDRV', 'TSLIB')  # Track mouse clicks on piTFT
        os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
        pygame.init()
        self.lcd = pygame.display.set_mode((320, 240))
        pygame.mouse.set_visible(False)
        self.font = pygame.font.Font(None, 30)  # Choose font size and type

    def get_processed_frame(self):
        frame = self.frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        return frame

    def update_from_camera(self, frame, roll_error=None):
        if frame is not None and not frame.size == 0:
            if roll_error is not None:
                rotation_matrix = cv2.getRotationMatrix2D((320, 240), -roll_error,
                                                          1)  # Subtract roll_error instead of adding it
                rotated_frame = cv2.warpAffine(frame, rotation_matrix, (640, 480))
                cropped_frame = rotated_frame[120:380, 100:500]
                self.frame = cropped_frame
                frame = cv2.resize(cropped_frame, (320, 240), interpolation=cv2.INTER_NEAREST)
                # Convert the color format from BGR to RGB for display with Pygame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB format for Pygame

            else:
                self.frame = frame
                frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_NEAREST)
                # Convert the color format from BGR to RGB for display with Pygame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB format for Pygame

            frame = np.rot90(frame)  # Rotate the frame
            frame = np.flipud(frame)  # Flip the frame
            surface = pygame.surfarray.make_surface(frame)

            # Convert the frame surface to the same format as the destination surface (self.lcd)
            surface = surface.convert(self.lcd)

            self.lcd.blit(surface, (0, 0))
            self.surface = surface

            if self.message and self.message_start_time:
                if time.time() - self.message_start_time < 2:
                    text_surface = self.font.render(self.message, True, (255, 255, 255))
                    text_width, text_height = text_surface.get_size()
                    text_position = (160 - text_width // 2, 120 - text_height // 2)
                    self.lcd.blit(text_surface, text_position)  # Position the message on the screen
                else:
                    self.message = None
                    self.message_start_time = None

            pygame.display.update()

        else:
            if self.surface is not None:
                self.lcd.blit(self.surface, (0, 0))
                pygame.display.update()

    def show_message(self, message):
        self.message = message
        self.message_start_time = time.time()
