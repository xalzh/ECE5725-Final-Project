import cv2

def draw_rectangle(event, x, y, flags, param):
    global roi, drawing, selected_roi

    if event == cv2.EVENT_LBUTTONDOWN:
        roi = [(x, y)]
        drawing = True
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            roi = [roi[0], (x, y)]
    elif event == cv2.EVENT_LBUTTONUP:
        roi.append((x, y))
        drawing = False
        selected_roi = True

        bbox = (roi[0][0], roi[0][1], abs(roi[1][0] - roi[0][0]), abs(roi[1][1] - roi[0][1]))
        tracker.init(frame, bbox)

cap = cv2.VideoCapture(0)

# Set the frame rate to 15 FPS
cap.set(cv2.CAP_PROP_FPS, 15)

cv2.namedWindow('frame')
cv2.setMouseCallback('frame', draw_rectangle)

roi = []
drawing = False
selected_roi = False
tracker = cv2.TrackerCSRT_create()

while True:
    ret, frame = cap.read()

    if ret:
        # Resize the frame to half its size
        frame = cv2.resize(frame, (frame.shape[1] // 2, frame.shape[0] // 2))

        if not selected_roi:
            if drawing and len(roi) == 2:
                cv2.rectangle(frame, roi[0], roi[1], (0, 255, 0), 2)
        else:
            ok, bbox = tracker.update(frame)
            if ok:
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(frame, p1, p2, (0, 255, 0), 2)

    cv2.imshow('frame', frame)

    # Increase the waitKey value to reduce CPU usage
    if cv2.waitKey(50) & 0xFF == ord('q'):
        break
