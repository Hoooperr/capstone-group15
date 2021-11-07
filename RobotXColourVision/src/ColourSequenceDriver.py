import os
import cv2
import numpy as np
import ColourRecognition as cr
import RectangleRecognition as rr

def on_change(value):
    """do nothing function"""
    pass

def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)

def main():
    cap = cv2.VideoCapture(1)
    cv2.namedWindow("Frame")
    cv2.namedWindow("Configuration", cv2.WINDOW_AUTOSIZE)
    image = np.zeros((45, 500, 3), np.uint8)    # placeholder image for configuration window
    image[:] = (0, 0, 0)
    cv2.imshow("Configuration", image)

    cv2.createTrackbar('focalLen', "Configuration", 500, 600, on_change)
    cv2.createTrackbar('width', "Configuration", 30, 50, on_change)
    cv2.createTrackbar('height', "Configuration", 18, 50, on_change)
    cv2.createTrackbar('red', "Configuration", 1, 1, on_change)
    cv2.createTrackbar('green', "Configuration", 1, 1, on_change)
    cv2.createTrackbar('blue', "Configuration", 1, 1, on_change)

    loading = 0
    sequence_list = []  # frame by frame sequence data
    final_sequence = [] # output of sequence recognition
    foundSequence = False
    frameRate = cap.get(cv2.CAP_PROP_FPS)/6

    while cap.isOpened():
        frameId = cap.get(1)
        ret, frame = cap.read()

        TARGET_WIDTH = cv2.getTrackbarPos("width", "Configuration")
        TARGET_HEIGHT = cv2.getTrackbarPos("height", "Configuration")
        RATIO = TARGET_HEIGHT / TARGET_WIDTH

        if ret:
            contours_red, contours_blue, contours_green, contours_black = cr.findRGBContours(frame)     

            # determines which colours to search for in each frame
            largest_contour = rr.getLargestContour(
                contours_red if cv2.getTrackbarPos("red", "Configuration") == 1 else [],
                contours_blue if cv2.getTrackbarPos("blue", "Configuration") == 1 else [],
                contours_green if cv2.getTrackbarPos("green", "Configuration") == 1 else [])

            isValidContour = True if (largest_contour and cv2.contourArea(largest_contour[0]) > 500) else False

            # Attempt to identify the colour sequence until it is successfully identified
            if not foundSequence and frameId % np.floor(frameRate) == 0:
                
                if loading <= 3:
                    clearConsole()
                    print("Capturing colour sequence" + "."*loading)
                    loading += 1
                else: 
                    loading = 0

                if isValidContour:
                    # choose the color with the largest area in the binary image as the main
                    sequence_list.append(largest_contour[1])
                else:
                    sequence_list.append("black")
                
                final_sequence, sequence_list = cr.detectColourSequence(sequence_list)
                
                foundSequence = True if final_sequence else False  

            if isValidContour: 

                rectangle = rr.getRectangle(largest_contour[0])

                # if shape has 4 sides it is a rectangle
                if rectangle.size > 0:
                    x, y, w, h = cv2.boundingRect(rectangle)

                    # (x,y) coordinates of each corner of shape
                    corner1 = np.array(rectangle[0]).flatten()
                    corner2 = np.array(rectangle[1]).flatten()
                    corner3 = np.array(rectangle[3]).flatten()
                    corner4 = np.array(rectangle[2]).flatten()

                    # vertical sides must be either left side or right side
                    if corner1[0] < corner4[0]:
                        left_side = np.array([corner1, corner2]) \
                            if rr.isVerticalLine(corner1, corner2) \
                            else np.array([corner1, corner3])

                        right_side = np.array([corner4, corner2]) \
                            if (left_side != np.array([corner1, corner2])).any() \
                            else np.array([corner4, corner3])
                    else:
                        left_side = np.array([corner4, corner2]) \
                            if (left_side != np.array([corner1, corner2])).any() \
                            else np.array([corner4, corner3])
                        
                        right_side = np.array([corner1, corner2]) \
                            if rr.isVerticalLine(corner1, corner2) \
                            else np.array([corner1, corner3])
                    
                    left_side_length = np.linalg.norm(np.subtract(left_side[0], left_side[1]))
                    right_side_length = np.linalg.norm(np.subtract(right_side[0], right_side[1]))

                    # distance between left and right sides
                    left_right_separation = rr.perpendicularWidth(left_side, right_side)

                    # Angle at which the targeted object is viewed from.
                    # Indicates to the vessel what direction it needs to move in 
                    # order to position itself directly in front of the object.
                    angle = -rr.calculateAngle(left_side_length, RATIO, left_right_separation) \
                        if left_side_length > right_side_length \
                        else rr.calculateAngle(right_side_length, RATIO, left_right_separation)

                    focal_len = cv2.getTrackbarPos("focalLen", "Configuration")
                    distance = (rr.distanceToObject(TARGET_HEIGHT, focal_len, left_side_length)
                                + rr.distanceToObject(TARGET_HEIGHT, focal_len, right_side_length)) / 2

                    # find the position of the targeted object relative to the centre of frame
                    frame_centrepoint = np.array((int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2),
                                            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)))
                    object_centrepoint = np.array((int(x+(w/2)), int(y+(h/2))))

                    # (x,y) x-component indicates which direction the vessel needs to turn in order to centre the object in frame.
                    # Negative x means turn left, positive x means turn right, zero means object is centre of frame.
                    pixels_from_centre = np.subtract(object_centrepoint, frame_centrepoint)

                    inPosition = True if (distance < 200 and abs(pixels_from_centre[0]) < 50 and abs(angle) < 10) else False

                    # search for target holes when vessel is close and centred in front of the correct dock
                    if foundSequence and inPosition:
                        # finds target holes (Dock and Deliver task)
                        targets = rr.findTargetHoles(contours_black)
                        if targets:
                            for target in targets:
                                (tx, ty, tw, th) = cv2.boundingRect(target)
                                cv2.rectangle(frame, (tx, ty), (tx+tw, ty+th), (0, 0, 255), 2)
                                cv2.putText(frame, "target", (tx + tw + 10, ty + th), 0, 0.5, (0, 0, 255))

                    # draw contours and text to the frame window
                    cv2.drawContours(frame, [rectangle], 0, (0, 255, 0), 2)
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
            # Terminate program - ESC
            if key == 27:
                break
            # Restart Sequence Capturing- P
            elif key == 80:
                foundSequence = False
            elif cv2.getWindowProperty("Frame", cv2.WND_PROP_VISIBLE) < 1:
                break
            elif cv2.getWindowProperty("Configuration", cv2.WND_PROP_VISIBLE) < 1:
                break

    cv2.destroyAllWindows()
    cap.release()

if __name__=="__main__":
    main()
