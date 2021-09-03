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

# Set a parameter, defined as the number of frames
timeF = 10
c = 1

# Determine the camera status. If return true means camera turn on success, false means fail.
while cap.isOpened():

    # ret and frame are two return values. ret is a boolean, frame is every frame of image
    ret, frame = cap.read()
    if ret:
        # ret and frame are two return values. ret is a boolean, frame is every frame of image
        ret, frame = cap.read()
        # Make sure the frame is not none
        if frame is not None:
            if c % timeF == 0:

                # Perform Gaussian Blur processing on the original image to facilitate color extraction.
                # (5,5) is the width and length of Gaussian Matrix
                # 0 is the standard of deviation
                gs_frame = cv2.GaussianBlur(frame, (5, 5), 0)

                # Convert Gaussian Blur image from BRG to HSV is more suitable for single color extraction.
                # OpenCV used rather BRG than RGB
                hsv = cv2.cvtColor(gs_frame, cv2.COLOR_BGR2HSV)

                # Make the image thinner and remover the noise in the image
                # Iteration represent the erode width
                erode_hsv = cv2.erode(hsv, None, iterations=2)

                # Remove other colors in the recognized colors convert the image as a binary image
                inRange_hsv = cv2.inRange(erode_hsv, color_dist['green']['Lower'], color_dist['green']['Upper'])

                # Save the binary image as a record to test
                cv2.imwrite("./Camera_image" + str(c/10) + '.jpg', inRange_hsv)

            c += 1

            # Show the frame
            cv2.imshow("camera", frame)
            k = cv2.waitKey(1)

            # If the 'q' key was pressed, break the loop
            if k == ord('q'):
                cap.release()
                break

        else:
            print("There is no views of camera")
    else:
        print("Unable connect the camera")
