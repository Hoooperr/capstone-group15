import cv2
import numpy as np
import ColourSequenceDriver as csd

def findRGBContours(frame):
    """Detects all the red, blue, green and black contours within the frame.
       returns all red, blue, green and black contours"""
    # dictionary containing the range of H(Hue), S(Saturation), V(Value) of red, green and blue
    # Edit these value to adjust the shades of each colour that recognised by the system.
    color_dist = {"red": {"Lower": np.array([0, 200, 46]), "Upper": np.array([12, 255, 255])},
                  "blue": {"Lower": np.array([100, 175, 100]), "Upper": np.array([113, 255, 255])},
                  "green": {"Lower": np.array([38, 60, 100]), "Upper": np.array([85, 255, 255])},
                  "black": {"Lower": np.array([0, 0, 0]), "Upper": np.array([180, 255, 50])}}

    # Perform Gaussian Blur processing on the original image to facilitate color extraction.
    # (5,5) is the width and length of Gaussian Matrix
    # 0 is the standard of deviation
    blurred = cv2.GaussianBlur(frame, (3, 3), 0)
    # Convert Gaussian Blur image from BRG to HSV is more suitable for single color extraction.
    # OpenCV used rather BRG than RGB
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    kernel = np.ones((5, 5), np.uint8)
    # Make the image thinner and remove the noise in the image
    # Iteration represent the erode width
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


def detectColourSequence(raw_sequence):
    temp_sequence = []
    detected_sequence = []
    
    if len(raw_sequence) < 100:
        # remove consecutive duplicate colours
        for i in range(len(raw_sequence)):
            if not temp_sequence or raw_sequence[i - 1] != raw_sequence[i]:
                temp_sequence.append(raw_sequence[i])

        # find the indexes of all black in temp_sequence
        black_indexes = [index for index, value in enumerate(temp_sequence) if value == "black"]
        if len(black_indexes) > 1:

            # if two non-consecutive black have been detected, take a slice between the two
            temp_sequence = temp_sequence[black_indexes[0] + 1:black_indexes[1]]

            # if slice has a length of 3 then it must contain the colour sequence
            if len(temp_sequence) == 3:
                detected_sequence = temp_sequence
                csd.clearConsole()
                print("SEQUENCE DETECTED")
                showSequence(detected_sequence)

            raw_sequence = []

    else: raw_sequence = []

    return detected_sequence, raw_sequence


def showSequence(sequence):
    colour_list = []
    for index in range(3):
        if sequence[index] == 'red':
            colour_list.append("\033[41m  \033[0m")
        elif sequence[index] == 'blue':
            colour_list.append("\033[44m  \033[0m")
        elif sequence[index] == 'green':
            colour_list.append("\033[42m  \033[0m")
    print(sequence)
    print("Scan the Code:\n" + colour_list[0] + "  " + colour_list[1] + "  " + colour_list[2])
    return
