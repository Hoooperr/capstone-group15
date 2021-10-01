import cv2
import numpy as np

def distanceToObject(known_width, focal_length, pixel_width):
    return (known_width * focal_length) / pixel_width


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

        largest_contour_area = None

        # find contour with largest area
        for contour in cnts_red:
            if largest_contour_area is None or cv2.contourArea(contour) > cv2.contourArea(largest_contour_area[0]):
                largest_contour_area = (contour, "red")

        for contour in cnts_blue:
            if largest_contour_area is None or cv2.contourArea(contour) > cv2.contourArea(largest_contour_area[0]):
                largest_contour_area = (contour, "blue")

        for contour in cnts_green:
            if largest_contour_area is None or cv2.contourArea(contour) > cv2.contourArea(largest_contour_area[0]):
                largest_contour_area = (contour, "green")

        if largest_contour_area is not None:

            # determine approximate shape
            epsilon = 0.03 * cv2.arcLength(largest_contour_area[0], True)
            poly_approx = cv2.approxPolyDP(largest_contour_area[0], epsilon, True)

            # if shape has 4 sides it is a rectangle
            if len(poly_approx) == 4 and cv2.contourArea(poly_approx) > 500:
                x, y, w, h = cv2.boundingRect(largest_contour_area[0])
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # find min area rectangle
                minRect = cv2.minAreaRect(largest_contour_area[0])
                box = cv2.boxPoints(minRect)
                box = np.int0(box)

                # vertical and horizontal lengths of rectangle
                side1 = np.linalg.norm(np.array(poly_approx[0]) - np.array(poly_approx[1]))
                side2 = np.linalg.norm(np.array(poly_approx[0]) - np.array(poly_approx[3]))

                # rectangle dimensions
                height = side1 if side1 < side2 else side2
                width = side1 if height != side1 else side2

                distance = distanceToObject(24, 520, width)

                # draw rectangle contour to frame
                cv2.drawContours(frame, [poly_approx], 0, (0, 255, 0), 2)
                cv2.putText(frame, "rectangle", (x + w + 10, y + h), 0, 0.5, (0, 255, 0))
                cv2.putText(frame, "%.2fcm" % distance, [int(x+(w/2)), int(y+(h/2))], 0, 0.5, (0, 255, 0))

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

cap.release()
cv2.destroyAllWindows()
