import cv2
import time
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

timeF = 10
c = 1

# Determine the camera status. If return true means camera turn on success, false means fail.
while cap.isOpened():

    # ret and frame are two return values. ret is a boolean, frame is every frame of image
    ret, frame = cap.read()
    if ret:
        ret, frame = cap.read()
        if frame is not None:
            if c % timeF == 0:
                cv2.imwrite("./Camera_image" + str(c/10) + '.jpg', frame)
            c += 1
            cv2.imshow("camera", frame)
            k = cv2.waitKey(1)
            if k == ord('q'):
                cap.release()
                break

        else:
            print("There is no views of camera")
    else:
        print("Unable connect the camera")
