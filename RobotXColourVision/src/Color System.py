import cv2
import numpy as np

# define a dictionary containing the range of H(Hue), S(Saturation), V(Value) of red, green and blue
color_dist = {"red": {"Lower": np.array([0, 60, 60]), "Upper": np.array([6, 255, 255])},
              "blue": {"Lower": np.array([100, 80, 46]), "Upper": np.array([124, 255, 255])},
              "green": {"Lower": np.array([35, 43, 35]), "Upper": np.array([90, 255, 255])}
              }

# Indicates the camera is turned on.
cap = cv2.VideoCapture(0)  # The parameter 0 in VideoCapture function is built-in camera
# cap = cv2.VideoCapture(1)  # The parameter 1 in VideoCapture USB external camera

# Named the window camera
cv2.namedWindow("camera")

while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        cv2.imshow("camera", frame)
    k = cv2.waitKey(1)
    if k == ord('q'):
        cap.release()
        break
