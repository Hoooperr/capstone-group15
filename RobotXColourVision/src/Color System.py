import cv2
import time
import datetime
import numpy as np


def output(list=[]):
    for i in range(0, 3):
        if list[i] == 'red':
            color = "\033[41m  \033[0m"
        if list[i] == 'blue':
            color = "\033[44m  \033[0m"
        if list[i] == 'green':
            color = "\033[42m  \033[0m"
    return "    Scan the Code   /n" + list[0] + "  " + list[1] + "  " + list[
        2] + "/n" + color + "  " + color + "  " + color


def nmea(list=[]):
    for i in range(0, 3):
        if list[i] == 'red':
            char = 'R'
        if list[i] == 'blue':
            char = 'B'
        if list[i] == 'green':
            char = 'G'
    date = datetime.datetime.now.strftime('%d%m%Y')
    time = datetime.datetime.now.strftime('%H%M%S')
    teamID = ''
    checksum = ''
    return "$RXCOD," + date + "," + time + teamID + "," + char + char + char + "*" + checksum


# define a dictionary containing the range of H(Hue), S(Saturation), V(Value) of red, green and blue
color_dist = {"red": {"Lower": np.array([0, 200, 60]), "Upper": np.array([10, 255, 255])},
              "blue": {"Lower": np.array([90, 60, 60]), "Upper": np.array([120, 255, 255])},
              "green": {"Lower": np.array([40, 40, 40]), "Upper": np.array([75, 255, 255])},
              "black": {"Lower": np.array([0, 0, 0]), "Upper": np.array([180, 255, 46])}
              }

# Indicates the camera is turned on.
# cap = cv2.VideoCapture(0)  # The parameter 0 in VideoCapture function is built-in camera
cap = cv2.VideoCapture(1)  # The parameter 1 in VideoCapture USB external camera

# Named the window camera
cv2.namedWindow("camera")

result = 0
area_blue = 0
area_red = 0
area_green = 0
area_black = 0
max_area = 0
count = 0
list = []

font = cv2.FONT_HERSHEY_SIMPLEX
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
                inRange_hsv_green = cv2.inRange(erode_hsv, color_dist['green']['Lower'], color_dist['green']['Upper'])
                inRange_hsv_red = cv2.inRange(erode_hsv, color_dist['red']['Lower'], color_dist['red']['Upper'])
                inRange_hsv_blue = cv2.inRange(erode_hsv, color_dist['blue']['Lower'], color_dist['blue']['Upper'])
                inRange_hsv_black = cv2.inRange(erode_hsv, color_dist['black']['Lower'], color_dist['black']['Upper'])

                # Use findContours function to detect the binary image to recognize the area
                contours_green, hierarchy_green = cv2.findContours(inRange_hsv_green, cv2.RETR_EXTERNAL,
                                                                   cv2.CHAIN_APPROX_NONE)
                contours_red, hierarchy_red = cv2.findContours(inRange_hsv_red, cv2.RETR_EXTERNAL,
                                                               cv2.CHAIN_APPROX_NONE)
                contours_blue, hierarchy_blue = cv2.findContours(inRange_hsv_blue, cv2.RETR_EXTERNAL,
                                                                 cv2.CHAIN_APPROX_NONE)
                contours_black, hierarchy_black = cv2.findContours(inRange_hsv_black, cv2.RETR_EXTERNAL,
                                                                   cv2.CHAIN_APPROX_NONE)

                # Define the initial area
                area_blue = 0
                area_red = 0
                area_green = 0
                area_black = 0

                # Calculate the area of different color in binary inage
                for i in contours_blue:
                    area_blue += cv2.contourArea(i)

                for i in contours_black:
                    area_black += cv2.contourArea(i)

                for i in contours_green:
                    area_green += cv2.contourArea(i)

                for i in contours_red:
                    area_red += cv2.contourArea(i)

                # print the color of max area in image
                result = max(area_blue, area_green, area_red, area_black)

                # choose the color with the largest area in the binary image as the main
                if result == area_blue:
                    if len(list) == 0:
                        list.append("blue")
                    else:
                        if list[-1] != "blue":
                            list.append("blue")

                if result == area_red:
                    if len(list) == 0:
                        list.append("red")
                    else:
                        if list[-1] != "red":
                            list.append("red")

                if result == area_green:
                    if len(list) == 0:
                        list.append("green")
                    else:
                        if list[-1] != "green":
                            list.append("green")

                if result == area_black:
                    if len(list) == 0:
                        list.append("black")
                    else:
                        if list[-1] != "black":
                            list.append("black")

                # find the color between two blacks as the correct color according to the array of color sequence
                blackCount = 0
                for i in list:
                    if i == "black":
                        blackCount += 1
                # print(list)
                if blackCount >= 2:
                    index1 = list.index("black")
                    index2 = list.index("black", index1 + 1)
                    sequence = list[index1 + 1:index2]
                    if len(sequence) == 3:
                        print(sequence)
                        #output(sequence)
                        #nmea(sequence)

                # Identify the color border
                for cnt in contours_green:
                    (x, y, w, h) = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    # Save the binary image as a record to test
                    cv2.imwrite("./Camera_image" + str(c / 10) + '.jpg', inRange_hsv_green)

                for cnt in contours_black:
                    (x, y, w, h) = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    # Save the binary image as a record to test
                    cv2.imwrite("./Camera_image" + str(c / 10) + '.jpg', inRange_hsv_black)

                for cnt1 in contours_blue:
                    (x1, y1, w1, h1) = cv2.boundingRect(cnt1)
                    cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 255), 2)
                    # Save the binary image as a record to test
                    cv2.imwrite("./Camera_image" + str(c / 10) + '.jpg', inRange_hsv_blue)

                for cnt2 in contours_red:
                    (x2, y2, w2, h2) = cv2.boundingRect(cnt2)
                    cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 255), 2)
                    # Save the binary image as a record to test
                    cv2.imwrite("./Camera_image" + str(c / 10) + '.jpg', inRange_hsv_red)

                # cv2.imshow("green", inRange_hsv_green)
                # cv2.imshow("blue", inRange_hsv_blue)
                # cv2.imshow("red", inRange_hsv_red)
                # cv2.imshow("black", inRange_hsv_black)
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