import cv2
import numpy as np

def findRGBContours(frame):
    # define a dictionary containing the range of H(Hue), S(Saturation), V(Value) of red, green and blue
    color_dist = {"red": {"Lower": np.array([0, 175, 60]), "Upper": np.array([15, 255, 255])},
                  "blue": {"Lower": np.array([95, 100, 60]), "Upper": np.array([120, 255, 255])},
                  "green": {"Lower": np.array([30, 60, 60]), "Upper": np.array([75, 255, 255])},
                  "black": {"Lower": np.array([0, 0, 0]), "Upper": np.array([180, 255, 50])}}

    # masking
    blurred = cv2.GaussianBlur(frame, (3, 3), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    kernel = np.ones((5, 5), np.uint8)
    erode = cv2.erode(hsv, kernel)

    # allows only objects of red, green or blue to appear in their respective frame
    hsv_red = cv2.inRange(erode, color_dist['red']['Lower'], color_dist['red']['Upper'])
    hsv_blue = cv2.inRange(erode, color_dist['blue']['Lower'], color_dist['blue']['Upper'])
    hsv_green = cv2.inRange(erode, color_dist['green']['Lower'], color_dist['green']['Upper'])
    hsv_black = cv2.inRange(erode, color_dist['black']['Lower'], color_dist['black']['Upper'])

    # get all contours for each colour
    contours_red, heir_red = cv2.findContours(hsv_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_blue, heir_blue = cv2.findContours(hsv_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_green, heir_green = cv2.findContours(hsv_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_black, heir_black = cv2.findContours(hsv_black, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return contours_red, contours_blue, contours_green, contours_black

def getLargestContour(c_red=[], c_blue=[], c_green=[], c_black=[]):
    """find contour with largest area"""
    largest_contour = []
    for contour in c_red:
        if largest_contour == [] or cv2.contourArea(contour) > cv2.contourArea(largest_contour[0]):
            largest_contour = (contour, "red")

    for contour in c_blue:
        if largest_contour == [] or cv2.contourArea(contour) > cv2.contourArea(largest_contour[0]):
            largest_contour = (contour, "blue")

    for contour in c_green:
        if largest_contour == [] or cv2.contourArea(contour) > cv2.contourArea(largest_contour[0]):
            largest_contour = (contour, "green")

    for contour in c_black:
        if largest_contour == [] or cv2.contourArea(contour) > cv2.contourArea(largest_contour[0]):
            largest_contour = (contour, "black")

    return largest_contour

def findTargetHoles(contours_black):
    """find and return the contours of the two target holes"""
    contours_black = sorted(contours_black, key=lambda x: cv2.contourArea(x), reverse=True)
    if len(contours_black) > 1:
        targets = contours_black[:2]
    elif len(contours_black) > 0:
        targets = contours_black[0]
    else:
        targets = []

    target_rects = []
    if len(targets) > 0:
        for contour in targets:
            # determine approximate shape
            epsilon = 0.03 * cv2.arcLength(contour, True)
            poly_approx = cv2.approxPolyDP(contour, epsilon, True)

            if len(poly_approx) == 4 and cv2.contourArea(poly_approx) > 500:
                target_rects.append(poly_approx)
            else:
                try:
                    targets.append(contours_black[len(targets)])
                except IndexError:
                    print("Only one target detected")
        return target_rects
    return []
