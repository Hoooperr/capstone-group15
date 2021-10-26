import numpy as np
import cv2

def getRectangle(contour):
    # determine approximate shape
    epsilon = 0.03 * cv2.arcLength(contour, True)
    poly_approx = cv2.approxPolyDP(contour, epsilon, True)

    if len(poly_approx) == 4:
        return poly_approx
    
    else:
        return np.array([])


def distanceToObject(known_width, focal_length, pixel_width):
    return (known_width * focal_length) / pixel_width


def isVerticalLine(pos1, pos2):
    return True if np.absolute(pos1[0] - pos2[0]) < np.absolute(pos1[1] - pos2[1]) else False


def perpendicularWidth(side1, side2):
    """shortest distance between parallel sides"""
    side1 = sorted(side1, key=lambda p: (p[1], p[0]))
    side2 = sorted(side2, key=lambda p: (p[1], p[0]))
    side1_midpoint = np.subtract(side1[1], np.divide(np.subtract(side1[1], side1[0]), 2))
    side2_midpoint = np.subtract(side2[1], np.divide(np.subtract(side2[1], side2[0]), 2))
    return np.linalg.norm(np.subtract(side1_midpoint, side2_midpoint))


def calculateAngle(perceived_height, ratio, perpendicular_width):
    pixel_width = perceived_height / ratio
    angle_increment = pixel_width / 90
    return 90 - perpendicular_width/angle_increment
