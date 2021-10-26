import numpy as np
import cv2
import ColourRecognition as cr
import datetime

def nmea(sequence=[]):
    char = []
    for i in range(3):
        if sequence[i] == 'red':
            char.append('R')
        if sequence[i] == 'blue':
            char.append('B')
        if sequence[i] == 'green':
            char.append('G')
    date = datetime.datetime.strftime('%d%m%Y')
    time = datetime.datetime.strftime('%H%M%S')
    teamID = 'teamID'
    checksum = 'checksum'
    return "$RXCOD," + date + "," + time + teamID + "," + char[0] + char[1] + char[2] + "*" + checksum


# Indicates the camera is turned on.
# cap = cv2.VideoCapture(0)  # The parameter 0 in VideoCapture function is built-in camera
cap = cv2.VideoCapture(0)  # The parameter 1 in VideoCapture USB external camera

# Named the window camera
cv2.namedWindow("camera")
sequence_list = []
final_sequence = []
foundSequence = False
# Set a parameter, defined as the number of frames
frameRate = cap.get(cv2.CAP_PROP_FPS)/6

# Determine the camera status. If return true means camera turn on success, false means fail.
while cap.isOpened():
    frameId = cap.get(1)
    # ret and frame are two return values. ret is a boolean, frame is every frame of image
    ret, frame = cap.read()
    if ret:
        if frameId % np.floor(frameRate) == 0:

            contours_red, contours_blue, contours_green, contours_black = cr.findRGBContours(frame)

            # print the color of max area in image
            result = cr.getLargestContour(contours_red, contours_blue, contours_green)

            if result and cv2.contourArea(result[0]) > 500:
                # choose the color with the largest area in the binary image as the main
                sequence_list.append(result[1])

                (x2, y2, w2, h2) = cv2.boundingRect(result[0])
                cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 255), 2)
            else:
                sequence_list.append("black")

            if not foundSequence:
                final_sequence, sequence_list = cr.detectColourSequence(sequence_list)
                foundSequence = True if final_sequence else False

        # Show the frame
        cv2.imshow("camera", frame)
        k = cv2.waitKey(1)

        # If the 'q' key was pressed, break the loop
        if k == ord('q'):
            cap.release()
            break
    else:
        print("Unable connect the camera")
