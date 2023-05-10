import cv2
import numpy as np

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

cap = cv2.VideoCapture(0)

cv2.namedWindow('frame')
cv2.setMouseCallback('frame', draw_rectangle)

roi = []
drawing = False
selected_roi = False
sift = cv2.SIFT_create()

while True:
    ret, frame = cap.read()

    if ret:
        if not selected_roi:
            if drawing and len(roi) == 2:
                cv2.rectangle(frame, roi[0], roi[1], (0, 255, 0), 2)
                roi_frame = frame[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]
        else:
            #roi_frame = frame[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]
            kp1, des1 = sift.detectAndCompute(roi_frame, None)

            kp2, des2 = sift.detectAndCompute(frame, None)
            bf = cv2.BFMatcher()
            matches = bf.knnMatch(des1, des2, k=2)

            good_matches = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)

            if len(good_matches) > 3:
                src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                if H is not None:
                    h, w = roi_frame.shape[:2]
                    roi_corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
                    frame_corners = cv2.perspectiveTransform(roi_corners, H)

                    frame = cv2.polylines(frame, [np.int32(frame_corners)], True, (0, 255, 0), 2)

            match_frame = cv2.drawMatches(roi_frame, kp1, frame, kp2, good_matches, None,
                                          flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            cv2.imshow('matches', match_frame)
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
