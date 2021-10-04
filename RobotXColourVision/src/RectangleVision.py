import cv2
import numpy as np
from ColourRecognition import findRGBContours

def distanceToObject(known_width, focal_length, pixel_width):
    return (known_width * focal_length) / pixel_width

def isVerticalLine(pos1, pos2):
    return True if np.absolute(pos1[0] - pos2[0]) < np.absolute(pos1[1] - pos2[1]) else False

def perpendicularDistance(side1, side2):
    side1 = sorted(side1, key=lambda p: (p[1], p[0]))
    side2 = sorted(side2, key=lambda p: (p[1], p[0]))

    side1_midpoint = np.subtract(side1[1], np.divide(np.subtract(side1[1], side1[0]), 2))
    side2_midpoint = np.subtract(side2[1], np.divide(np.subtract(side2[1], side2[0]), 2))

    return np.linalg.norm(np.subtract(side1_midpoint, side2_midpoint))

def calculateAngle(perpendicular_width, actual_width):

    return actual_width


cap = cv2.VideoCapture(0)
TARGET_WIDTH = 30  # cm
TARGET_HEIGHT = 18  # cm

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
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 232, 226), 2)

                # find min area rectangle
                minRect = cv2.minAreaRect(largest_contour_area[0])
                box = cv2.boxPoints(minRect)
                box = np.int0(box)

                corner1 = np.array(poly_approx[0]).flatten()
                corner2 = np.array(poly_approx[1]).flatten()
                corner3 = np.array(poly_approx[3]).flatten()
                corner4 = np.array(poly_approx[2]).flatten()

                # vertical and horizontal lengths of rectangle
                side_length1 = np.linalg.norm(np.subtract(corner1, corner2))
                side_length2 = np.linalg.norm(np.subtract(corner1, corner3))
                side_length3 = np.linalg.norm(np.subtract(corner4, corner2))
                side_length4 = np.linalg.norm(np.subtract(corner4, corner3))

                left_side = np.array([corner1, corner2]) \
                    if isVerticalLine(corner1, corner2) \
                    else np.array([corner1, corner3])

                right_side = np.array([corner4, corner2]) \
                    if (left_side != np.array([corner1, corner2])).any() \
                    else np.array([corner4, corner3])

                left_side_length = np.linalg.norm(np.subtract(left_side[0], left_side[1]))
                right_side_length = np.linalg.norm(np.subtract(right_side[0], right_side[1]))

                # print(perpendicularDistance(left_side, right_side))

                height = side_length1 if isVerticalLine(corner1, corner2) else side_length2
                width = side_length1 if height != side_length1 else side_length2

                distance = (distanceToObject(TARGET_HEIGHT, 430, left_side_length) + distanceToObject(TARGET_HEIGHT, 430, right_side_length)) / 2

                # draw rectangle contour to frame
                cv2.drawContours(frame, [poly_approx], 0, (0, 232, 226), 2)

                cv2.putText(frame, "rectangle", (x + w + 10, y + h), 0, 0.5, (0, 232, 226))
                cv2.putText(frame, "%.2fcm" % distance, [int(x+(w/2)), int(y+(h/2))], 0, 0.5, (0, 232, 226))

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

cap.release()
cv2.destroyAllWindows()
