import cv2
import numpy as np

# define a dictionary containing the range of H(Hue), S(Saturation), V(Value) of red, green and blue
color_dist = {"red": {"Lower": np.array([0, 200, 60]), "Upper": np.array([10, 255, 255])},
              "blue": {"Lower": np.array([90, 60, 60]), "Upper": np.array([120, 255, 255])},
              "green": {"Lower": np.array([40, 40, 40]), "Upper": np.array([75, 255, 255])}
              }

# Indicates the camera is turned on.
cap = cv2.VideoCapture(0)  # The parameter 0 in VideoCapture function is built-in camera
# cap = cv2.VideoCapture(1)  # The parameter 1 in VideoCapture USB external camera

# Named the window camera
cv2.namedWindow("camera")

result = 0
area_blue = 0
area_red = 0
area_green = 0
max_area = 0
array = ["black"]
count = 0

font = cv2.FONT_HERSHEY_SIMPLEX
# Set a parameter, defined as the number of frames

# Determine the camera status. If return true means camera turn on success, false means fail.
while cap.isOpened():

    # ret and frame are two return values. ret is a boolean, frame is every frame of image
    ret, frame = cap.read()
    if ret:
        # ret and frame are two return values. ret is a boolean, frame is every frame of image
        ret, frame = cap.read()
        # Make sure the frame is not none
        if frame is not None:

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

            # Use findContours function to detect the binary image to reconigize the area
            contours_green, hierarchy_green = cv2.findContours(inRange_hsv_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            contours_red, hierarchy_red = cv2.findContours(inRange_hsv_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            contours_blue, hierarchy_blue = cv2.findContours(inRange_hsv_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            # Define the initial area
            area_blue = 0
            area_red = 0
            area_green = 0

            # Calculate the area of different color in binary inage
            for i in contours_blue:
                area_blue += cv2.contourArea(i)

            for i in contours_green:
                area_green += cv2.contourArea(i)

            for i in contours_red:
                area_red += cv2.contourArea(i)

            # print the color of max area in image
            result = max(area_blue, area_green, area_red)

            #for j in range(3):

            if result == area_blue:
                if array[count] != "blue":
                    if count >= 3:
                            newAr = []
                            newAr.append("blue")
                            newAr.append(array[0])
                            newAr.append(array[1])
                            array[0] = newAr[0]
                            array[1] = newAr[1]
                            array[2] = newAr[2]
                            count = 3
                            #array.append("blue")
                        else:
                            array.append("blue")
                            count=count + 1
                    print(array)

                if result == area_red:
                    if array[count] != "red":
                        if count >= 3:
                            newAr = []
                            newAr.append("red")
                            newAr.append(array[0])
                            newAr.append(array[1])
                            array[0] = newAr[0]
                            array[1] = newAr[1]
                            array[2] = newAr[2]
                            count = 3
                            #array.append("blue")
                        else:
                            array.append("red")
                            count=count + 1
                    print(array)

                if result == area_green:
                    if array[count] != "green":
                        if count >= 3:
                            newAr = []
                            newAr.append("green")
                            newAr.append(array[0])
                            newAr.append(array[1])
                            array[0] = newAr[0]
                            array[1] = newAr[1]
                            array[2] = newAr[2]
                            count = 3
                            #array.append("blue")
                        else:
                            array.append("green")
                            count=count + 1
                    print(array)

                # Identify the color border
                for cnt in contours_green:
                    (x, y, w, h) = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    #print("green")
                    # Save the binary image as a record to test
                    cv2.imwrite("./Camera_image" + str(c / 10) + '.jpg', inRange_hsv_green)

                for cnt1 in contours_blue:
                    (x1, y1, w1, h1) = cv2.boundingRect(cnt1)
                    cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 255), 2)
                    #print("blue")
                    # Save the binary image as a record to test
                    cv2.imwrite("./Camera_image" + str(c / 10) + '.jpg', inRange_hsv_blue)

                for cnt2 in contours_red:
                    (x2, y2, w2, h2) = cv2.boundingRect(cnt2)
                    cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 255), 2)
                    #print("red")
                    # Save the binary image as a record to test
                    cv2.imwrite("./Camera_image" + str(c / 10) + '.jpg', inRange_hsv_red)

                #cv2.imshow("green", inRange_hsv_green)
                #cv2.imshow("blue", inRange_hsv_blue)
                #cv2.imshow("red", inRange_hsv_red)
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
