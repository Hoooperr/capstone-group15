import cv2
import numpy as np

def findRGBContours(frame):
    # define a dictionary containing the range of H(Hue), S(Saturation), V(Value) of red, green and blue
    color_dist = {"red": {"Lower": np.array([0, 175, 60]), "Upper": np.array([15, 255, 255])},
                  "blue": {"Lower": np.array([95, 100, 60]), "Upper": np.array([120, 255, 255])},
                  "green": {"Lower": np.array([30, 60, 60]), "Upper": np.array([75, 255, 255])}
                  }
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
    contours_red, heir_red = cv2.findContours(hsv_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_blue, heir_blue = cv2.findContours(hsv_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_green, heir_green = cv2.findContours(hsv_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return contours_red, contours_blue, contours_green
