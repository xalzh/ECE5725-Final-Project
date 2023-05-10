import pygame
from pygame.locals import *
import os
import time
import RPi.GPIO as GPIO
import threading


class ui(threading.Thread):
    def __init__(self, ready_event, terminate_event, button17_event, button22_event, button23_event):
        super().__init__()
        self.ready_event = ready_event
        self.button17_event = button17_event
        self.button22_event = button22_event
        self.button23_event = button23_event
        self.button27_event = terminate_event
        self.button_pins = [17, 22, 23, 27]  # Define the GPIO pins for the four buttons

    def run(self):
        GPIO.setmode(GPIO.BCM)
        for pin in self.button_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        while not self.ready_event.is_set():
            for pin in self.button_pins:
                if GPIO.input(pin) == GPIO.LOW:
                    self.perform_task(pin)
                    time.sleep(0.2)  # Debouncing

    def perform_task(self, pin):
        if pin == self.button_pins[0]:
            print("Button 1 pressed: Task 1")
            self.button17_event.set()
        elif pin == self.button_pins[1]:
            print("Button 2 pressed: Task 2")
            self.button22_event.set()
        elif pin == self.button_pins[2]:
            print("Button 3 pressed: Task 3")
            self.button23_event.set()
        elif pin == self.button_pins[3]:
            print("Button 4 pressed: Terminating all programs")
            self.button27_event.set()
