import os
import cv2

os.environ["SDL_VIDEODRIVER"] = "fbcon"
os.putenv('SDL_FBDEV', '/dev/fb0')  #
os.putenv('SDL_MOUSEDRV', 'TSLIB')  # Track mouse clicks on piTFT
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')


# Use the 0th camera attached to the system
cap = cv2.VideoCapture(0)

# Set the resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Display the resulting frame
    cv2.imshow('Camera Feed', frame)

    # Wait for 1 millisecond, break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture and destroy the window
cap.release()
cv2.destroyAllWindows()
