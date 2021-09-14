import cv2
import numpy as np

# define a dictionary containing the range of H(Hue), S(Saturation), V(Value) of red, green and blue
color_dist = {"red": {"Lower": np.array([0, 150, 60]), "Upper": np.array([10, 255, 255])},
              "blue": {"Lower": np.array([95, 100, 60]), "Upper": np.array([120, 255, 255])},
              "green": {"Lower": np.array([30, 60, 60]), "Upper": np.array([75, 255, 255])}
              }

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        # masking
        blurred = cv2.GaussianBlur(frame, (3, 3), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        kernel = np.ones((5, 5), np.uint8)
        erode = cv2.erode(hsv, kernel)

        # allows only objects of red, green or blue to appear in their respective frame
        hsv_red = cv2.inRange(erode, color_dist['red']['Lower'], color_dist['red']['Upper'])
        hsv_blue = cv2.inRange(erode, color_dist['blue']['Lower'], color_dist['blue']['Upper'])
        hsv_green = cv2.inRange(erode, color_dist['green']['Lower'], color_dist['green']['Upper'])

        # get all contours for each colour
        cnts_red, heir_red = cv2.findContours(hsv_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts_blue, heir_blue = cv2.findContours(hsv_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts_green, heir_green = cv2.findContours(hsv_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        max_cnt = None

        # find contour with largest area
        for cnt in cnts_red:
            if max_cnt is None or cv2.contourArea(cnt) > cv2.contourArea(max_cnt[0]):
                max_cnt = (cnt, "red")

        for cnt in cnts_blue:
            if max_cnt is None or cv2.contourArea(cnt) > cv2.contourArea(max_cnt[0]):
                max_cnt = (cnt, "blue")

        #
        for cnt in cnts_green:
            if max_cnt is None or cv2.contourArea(cnt) > cv2.contourArea(max_cnt[0]):
                max_cnt = (cnt, "green")

        if max_cnt is not None:
            x, y, w, h = cv2.boundingRect(max_cnt[0])
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # find min area rectangle
            minRect = cv2.minAreaRect(max_cnt[0])
            box = cv2.boxPoints(minRect)
            box = np.int0(box)

            shape_text = max_cnt[1]

            # determine if shape is a rectangle
            epsilon = 0.03 * cv2.arcLength(max_cnt[0], True)
            poly_approx = cv2.approxPolyDP(max_cnt[0], epsilon, True)
            if len(poly_approx) == 4:
                shape_text += " rectangle"

            # draw rectangle contour to frame
            cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)
            cv2.putText(frame, shape_text, (x+w+10, y+h), 0, 0.5, (0, 255, 0))
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

cap.release()
cv2.destroyAllWindows()
