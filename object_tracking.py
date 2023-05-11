"""
4/16/2023 by Zehao Li

This class implements the MOSSE algorithm and opens a window for the user to select a Region
of Interest (ROI). Once an ROI is selected, the algorithm tracks the ROI using the MOSSE tracker and returns the
coordinates of the tracked box.

Functions:
- save_initial_roi_frame(frame): Saves the initial region of interest (ROI) frame and ROI.
- handle_touch_event(event): Handles touch events for selecting the ROI.
- run(frame): Executes the MOSSE algorithm by selecting the ROI and performing tracking.
"""

import cv2
import os
import pygame
from pygame.locals import *


class MOSSE():
    def __init__(self):
        self.initial_roi = None
        self.tracker = None
        self.initial_roi_frame = None
        self.roi = []
        self.finger_touch = True
        self.drawing = False
        self.selected_roi = False
        self.roi_lost = False
        pygame.init()
        pygame.mouse.set_visible(False)
        self.lcd = pygame.display.set_mode((320, 240))
        pygame.display.update()

    def save_initial_roi_frame(self, frame):
        # Save the initial region of interest (ROI) frame and ROI
        if len(self.roi) == 2:
            self.initial_roi_frame = frame.copy()  # Save the original frame
            self.initial_roi = frame[self.roi[0][1]:self.roi[1][1], self.roi[0][0]:self.roi[1][0]]

    def handle_touch_event(self, event):
        # Handle touch events for selecting ROI
        if event.type == MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if not self.drawing:
                # Reset selected_roi flag when starting to draw a new ROI
                self.selected_roi = False
                self.roi = [(pos[0] * 2, pos[1] * 2)]
                self.drawing = True
        elif event.type == MOUSEMOTION:
            if self.drawing:
                # If currently drawing an ROI, update the end point of the ROI to the current mouse position
                pos = pygame.mouse.get_pos()
                self.roi[1:] = [(pos[0] * 2, pos[1] * 2)]
        elif event.type == MOUSEBUTTONUP:
            # When the mouse button is released, stop drawing the ROI
            pos = pygame.mouse.get_pos()
            self.roi.append((pos[0] * 2, pos[1] * 2))
            self.drawing = False
            # Calculate the width and height of the selected ROI
            roi_width = abs(self.roi[1][0] - self.roi[0][0])
            roi_height = abs(self.roi[1][1] - self.roi[0][1])
            # Check if the selected ROI is too small (less than 5 pixels in width or height)
            if roi_width < 5 or roi_height < 5:
                # Reset the ROI and set selected_roi to False
                self.roi = []
                self.selected_roi = False
            else:
                self.selected_roi = True
                self.finger_touch = False
                # Update the ROI coordinates to ensure the top-left and bottom-right points are correct
                self.roi = [(min([self.roi[0][0], self.roi[1][0]]), min([self.roi[0][1], self.roi[1][1]])),
                            (max([self.roi[0][0], self.roi[1][0]]), max([self.roi[0][1], self.roi[1][1]]))]

    def run(self, frame):
        roi = self.roi
        selected_roi = self.selected_roi
        drawing = self.drawing
        # Handle touch events if finger_touch flag is True
        if self.finger_touch:
            for event in pygame.event.get():
                self.handle_touch_event(event)
        # If no ROI is selected, draw the selection rectangle
        if not selected_roi:
            if drawing and len(roi) == 2:
                cv2.rectangle(frame, roi[0], roi[1], (0, 255, 0), 2)
                roi_frame = frame[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]
        # If an ROI is selected, initialize the tracker and update the ROI coordinates
        else:
            if not hasattr(self, 'tracker'):
                roi_width = abs(roi[1][0] - roi[0][0])
                roi_height = abs(roi[1][1] - roi[0][1])
                if roi_width <= 1 or roi_height <= 1:
                    # Reset the ROI and set selected_roi to False
                    self.roi = []
                    self.selected_roi = False
                    return frame, None, False, False
                # Create a MOSSE tracker and initialize it with the current frame and ROI bounding box
                self.tracker = cv2.legacy.TrackerMOSSE_create()
                bbox = (roi[0][0], roi[0][1], roi_width, roi_height)
                self.tracker.init(frame, bbox)
            else:
                # Update the tracker with the current frame
                success, bbox = self.tracker.update(frame)
                if success:
                    # If tracking is successful, draw the bounding box on the frame
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv2.rectangle(frame, p1, p2, (0, 255, 0), 2)
                    # Update the roi variable with the new coordinates
                    roi = [p1, p2]
                    self.roi_lost = False
                else:
                    # If tracking fails, set the roi_lost flag to True
                    self.roi_lost = True
        # Return the updated frame, ROI coordinates, and flags
        return frame, roi, self.selected_roi, self.roi_lost
