import numpy as np
import cv2

def getLargestContour(c_red=[], c_blue=[], c_green=[], c_black=[]):
    """find contour with largest area"""
    largest_contour = ()
    for contour in c_red:
        if (not largest_contour or cv2.contourArea(contour) > cv2.contourArea(largest_contour[0])) and getRectangle(contour).size > 0:
            largest_contour = (contour, "red")

    for contour in c_blue:
        if (not largest_contour or cv2.contourArea(contour) > cv2.contourArea(largest_contour[0])) and getRectangle(contour).size > 0:
            largest_contour = (contour, "blue")

    for contour in c_green:
        if (not largest_contour or cv2.contourArea(contour) > cv2.contourArea(largest_contour[0])) and getRectangle(contour).size > 0:
            largest_contour = (contour, "green")

    for contour in c_black:
        if (not largest_contour or cv2.contourArea(contour) > cv2.contourArea(largest_contour[0])) and getRectangle(contour).size > 0:
            largest_contour = (contour, "black")

    return largest_contour

def getRectangle(contour):
    # determine approximate shape
    epsilon = 0.03 * cv2.arcLength(contour, True)
    poly_approx = cv2.approxPolyDP(contour, epsilon, True)

    if len(poly_approx) == 4:
        return poly_approx
    
    else:
        return np.array([])

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
                    pass
        return target_rects
    return []

def distanceToObject(known_width, focal_length, pixel_width):
    return (known_width * focal_length) / pixel_width


def isVerticalLine(a, b):
    """returns true if the x difference is less than the y difference"""
    return True if np.absolute(a[0] - b[0]) < np.absolute(a[1] - b[1]) else False


def perpendicularWidth(side1, side2):
    """the distance between parallel sides"""
    side1 = sorted(side1, key=lambda p: (p[1], p[0]))
    side2 = sorted(side2, key=lambda p: (p[1], p[0]))
    side1_midpoint = np.subtract(side1[1], np.divide(np.subtract(side1[1], side1[0]), 2))
    side2_midpoint = np.subtract(side2[1], np.divide(np.subtract(side2[1], side2[0]), 2))
    return np.linalg.norm(np.subtract(side1_midpoint, side2_midpoint))


def calculateAngle(perceived_height, ratio, perpendicular_width):
    pixel_width = perceived_height / ratio
    angle_increment = pixel_width / 90
    return 90 - perpendicular_width/angle_increment
