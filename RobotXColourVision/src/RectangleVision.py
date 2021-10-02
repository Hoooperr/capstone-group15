import cv2
import numpy as np
from ColourRecognition import findRGBContours

def distanceToObject(known_width, focal_length, pixel_width):
    return (known_width * focal_length) / pixel_width

def isVerticalLine(pos1, pos2):
    return True if np.absolute(pos1[0] - pos2[0]) < np.absolute(pos1[1] - pos2[1]) else False


cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    if ret:

        # get all contours for each colour
        contours_red, contours_blue, contours_green = findRGBContours(frame)

        largest_contour_area = None

        # find contour with largest area
        for contour in contours_red:
            if largest_contour_area is None or cv2.contourArea(contour) > cv2.contourArea(largest_contour_area[0]):
                largest_contour_area = (contour, "red")

        for contour in contours_blue:
            if largest_contour_area is None or cv2.contourArea(contour) > cv2.contourArea(largest_contour_area[0]):
                largest_contour_area = (contour, "blue")

        for contour in contours_green:
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

                corner1 = np.array(poly_approx[0]).flatten()
                corner2 = np.array(poly_approx[1]).flatten()
                corner3 = np.array(poly_approx[3]).flatten()

                # vertical and horizontal lengths of rectangle
                side1 = np.linalg.norm(corner1 - corner2)
                side2 = np.linalg.norm(corner1 - corner3)

                height = side1 if isVerticalLine(corner1, corner2) else side2
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
