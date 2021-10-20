import cv2
import numpy as np
import ColourRecognition as cr

def distanceToObject(known_width, focal_length, pixel_width):
    return (known_width * focal_length) / pixel_width


def isVerticalLine(pos1, pos2):
    return True if np.absolute(pos1[0] - pos2[0]) < np.absolute(pos1[1] - pos2[1]) else False


def perpendicularWidth(side1, side2):
    """shortest path between parallel sides"""
    side1 = sorted(side1, key=lambda p: (p[1], p[0]))
    side2 = sorted(side2, key=lambda p: (p[1], p[0]))
    side1_midpoint = np.subtract(side1[1], np.divide(np.subtract(side1[1], side1[0]), 2))
    side2_midpoint = np.subtract(side2[1], np.divide(np.subtract(side2[1], side2[0]), 2))
    return np.linalg.norm(np.subtract(side1_midpoint, side2_midpoint))


def calculateAngle(perceived_height, ratio, perpendicular_width):
    pixel_width = perceived_height / ratio
    angle_increment = pixel_width / 90
    return 90 - perpendicular_width/angle_increment

def on_change(value):
    """do nothing function"""
    pass


cap = cv2.VideoCapture(0)
cv2.namedWindow("Frame")
cv2.namedWindow("Configuration", cv2.WINDOW_AUTOSIZE)
image = np.zeros((45, 500, 3), np.uint8)
image[:] = (0, 0, 0)      # placeholder for trackbars
cv2.imshow("Configuration", image)

cv2.createTrackbar('focalLen', "Configuration", 500, 600, on_change)
cv2.createTrackbar('width', "Configuration", 30, 50, on_change)
cv2.createTrackbar('height', "Configuration", 18, 50, on_change)
cv2.createTrackbar('red', "Configuration", 1, 1, on_change)
cv2.createTrackbar('green', "Configuration", 1, 1, on_change)
cv2.createTrackbar('blue', "Configuration", 1, 1, on_change)

while cap.isOpened():
    ret, frame = cap.read()

    TARGET_WIDTH = cv2.getTrackbarPos("width", "Configuration")
    TARGET_HEIGHT = cv2.getTrackbarPos("height", "Configuration")
    RATIO = TARGET_HEIGHT / TARGET_WIDTH

    if ret:
        contours_red, contours_blue, contours_green, contours_black = cr.findRGBContours(frame)

        largest_contour = cr.getLargestContour(
            contours_red if cv2.getTrackbarPos("red", "Configuration") == 1 else [],
            contours_blue if cv2.getTrackbarPos("blue", "Configuration") == 1 else [],
            contours_green if cv2.getTrackbarPos("green", "Configuration") == 1 else [])

        if largest_contour != []:

            # determine approximate shape
            epsilon = 0.03 * cv2.arcLength(largest_contour[0], True)
            poly_approx = cv2.approxPolyDP(largest_contour[0], epsilon, True)

            # if shape has 4 sides it is a rectangle
            if len(poly_approx) == 4 and cv2.contourArea(poly_approx) > 500:
                x, y, w, h = cv2.boundingRect(largest_contour[0])

                # (x,y) coordinates of each corner of shape
                corner1 = np.array(poly_approx[0]).flatten()
                corner2 = np.array(poly_approx[1]).flatten()
                corner3 = np.array(poly_approx[3]).flatten()
                corner4 = np.array(poly_approx[2]).flatten()

                # vertical sides must be either left side or right side
                left_side = np.array([corner1, corner2]) \
                    if isVerticalLine(corner1, corner2) \
                    else np.array([corner1, corner3])

                right_side = np.array([corner4, corner2]) \
                    if (left_side != np.array([corner1, corner2])).any() \
                    else np.array([corner4, corner3])

                left_side_length = np.linalg.norm(np.subtract(left_side[0], left_side[1]))
                right_side_length = np.linalg.norm(np.subtract(right_side[0], right_side[1]))

                # distance between left and right sides
                left_right_separation = perpendicularWidth(left_side, right_side)

                # angle at which the targeted object is viewed from
                angle = -calculateAngle(left_side_length, RATIO, left_right_separation) \
                    if left_side_length >= right_side_length \
                    else calculateAngle(right_side_length, RATIO, left_right_separation)

                focal_len = cv2.getTrackbarPos("focalLen", "Configuration")
                distance = (distanceToObject(TARGET_HEIGHT, focal_len, left_side_length)
                            + distanceToObject(TARGET_HEIGHT, focal_len, right_side_length)) / 2

                # find the position of the targeted object relative to the centre of frame
                frame_midpoint = np.array((int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2),
                                           int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)))
                object_midpoint = np.array((int(x+(w/2)), int(y+(h/2))))
                pixels_from_centre = np.subtract(object_midpoint, frame_midpoint)

                # search for target holes when vessel is close and centred in front of the correct dock
                if distance < 200 and abs(pixels_from_centre[0]) < 50 and abs(angle) < 10:
                    # finds target holes (Dock and Deliver task)
                    targets = cr.findTargetHoles(contours_black)
                    if targets != []:
                        for target in targets:
                            (tx, ty, tw, th) = cv2.boundingRect(target)
                            cv2.rectangle(frame, (tx, ty), (tx+tw, ty+th), (0, 0, 255), 2)
                            cv2.putText(frame, "target", (tx + tw + 10, ty + th), 0, 0.5, (0, 0, 255))

                # draw rectangle contour to frame
                cv2.drawContours(frame, [poly_approx], 0, (0, 255, 0), 2)

                cv2.putText(frame, largest_contour[1], (x + w + 10, y + h), 0, 0.5, (0, 255, 0))
                cv2.putText(frame, "%.2fcm" % distance, [int(x+(w/2)), int(y+(h/2))], 0, 0.5, (0, 255, 0))
                cv2.putText(frame, "Viewing angle: %.2fdeg" % angle,
                            [10, int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) - 50],
                            0, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Position from centre: {}".format(pixels_from_centre),
                            [10, int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) - 20],
                            0, 0.7, (0, 255, 0), 2)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
        elif cv2.getWindowProperty("Frame", cv2.WND_PROP_VISIBLE) < 1:
            break
        elif cv2.getWindowProperty("Configuration", cv2.WND_PROP_VISIBLE) < 1:
            break

cv2.destroyAllWindows()
cap.release()
