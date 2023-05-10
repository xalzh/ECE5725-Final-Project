import cv2

def main():
    # Open the default camera (usually the first one connected)
    cap = cv2.VideoCapture(0)

    # Check if the camera was opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Check if the frame was captured correctly
        if not ret:
            print("Error: Could not read frame from camera")
            break

        # Display the resulting frame
        cv2.imshow('Camera Feed', frame)

        # Exit the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
