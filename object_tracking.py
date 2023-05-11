"""
4/16/2023 by Zehao Li
This class implements the MOSSE algorithm and open a window ready for the user to select ROI. After the ROI is selected,
the algorithm will try to track the ROI and return the coordinates of the box.
"""

import cv2
import os
import pygame
from pygame.locals import *


class MOSSE():
    def __init__(self):
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
        if len(self.roi) == 2:
            self.initial_roi_frame = frame.copy()  # Save the original frame
            self.initial_roi = frame[self.roi[0][1]:self.roi[1][1], self.roi[0][0]:self.roi[1][0]]

    def handle_touch_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if not self.drawing:
                # Reset selected_roi flag when starting to draw a new ROI
                self.selected_roi = False
                self.roi = [(pos[0] * 2, pos[1] * 2)]
                self.drawing = True
        elif event.type == MOUSEMOTION:
            if self.drawing:
                pos = pygame.mouse.get_pos()
                self.roi[1:] = [(pos[0] * 2, pos[1] * 2)]
        elif event.type == MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            self.roi.append((pos[0] * 2, pos[1] * 2))
            self.drawing = False

            # Calculate the width and height of the selected ROI
            roi_width = abs(self.roi[1][0] - self.roi[0][0])
            roi_height = abs(self.roi[1][1] - self.roi[0][1])

            # Check if the selected ROI is too small (e.g., less than 5 pixels in width or height)
            if roi_width < 5 or roi_height < 5:
                # Reset the ROI and set selected_roi to False
                self.roi = []
                self.selected_roi = False
            else:
                self.selected_roi = True
                self.finger_touch = False
                self.roi = [(min([self.roi[0][0], self.roi[1][0]]), min([self.roi[0][1], self.roi[1][1]])),
                            ((max([self.roi[0][0], self.roi[1][0]]), max([self.roi[0][1], self.roi[1][1]])))]

    def run(self, frame):
        roi = self.roi
        selected_roi = self.selected_roi
        drawing = self.drawing

        if self.finger_touch:
            for event in pygame.event.get():
                self.handle_touch_event(event)

        if not selected_roi:
            if drawing and len(roi) == 2:
                cv2.rectangle(frame, roi[0], roi[1], (0, 255, 0), 2)
                roi_frame = frame[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]
        else:
            if not hasattr(self, 'tracker'):
                roi_width = abs(roi[1][0] - roi[0][0])
                roi_height = abs(roi[1][1] - roi[0][1])

                if roi_width <= 1 or roi_height <= 1:
                    # Reset the ROI and set selected_roi to False
                    self.roi = []
                    self.selected_roi = False
                    return frame, None, False, False

                self.tracker = cv2.legacy.TrackerMOSSE_create()
                bbox = (roi[0][0], roi[0][1], roi_width, roi_height)
                self.tracker.init(frame, bbox)
            else:
                success, bbox = self.tracker.update(frame)
                if success:
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv2.rectangle(frame, p1, p2, (0, 255, 0), 2)
                    # Update the roi variable with the new coordinates
                    roi = [p1, p2]
                    self.roi_lost = False
                else:
                    self.roi_lost = True

        return frame, roi, self.selected_roi, self.roi_lost
