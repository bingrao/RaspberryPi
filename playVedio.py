#!/usr/bin/env python
import cv2


if __name__ == "__main__":
    cap = cv2.VideoCapture('output.avi')

    if not cap.isOpened():
        print("The Camera is not open ...\n")
        cap.open()

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret is True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            print("Frame capture failed, stopping...\n")
            break;


        cv2.imshow('Source Image', frame)

        c = cv2.waitKey(5)
        if c == 27:
            print("ESC detected, stopping...\n")
        break

    cap.release()
    cv2.destroyAllWindows()
