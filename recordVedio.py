#!/usr/bin/env python
import cv2

if __name__ == "__main__":
    # find the webcam
    capture = cv2.VideoCapture(0)
	
    if not capture.isOpened():
        print("The Camera is not open ...\n")
        capture.open()
	
    CV_CAP_PROP_FRAME_WIDTH = 3
    CV_CAP_PROP_FRAME_HEIGHT = 4
    capture.set(CV_CAP_PROP_FRAME_WIDTH, 240);
    capture.set(CV_CAP_PROP_FRAME_HEIGHT, 320);
    
	
	# video recorder
    fourcc = cv2.cv.CV_FOURCC(*'XVID')  # cv2.VideoWriter_fourcc() does not exist
    video_writer = cv2.VideoWriter("output.avi", fourcc, 20, (240, 320))

    # record video
    while (capture.isOpened()):
        ret, frame = capture.read()
        if ret:
            video_writer.write(frame)
            cv2.imshow('Video Stream', frame)
        else:
            break
			
        c = cv2.waitKey(1)
        if c == 27:
            print("ESC detected, stopping...\n")
            break	
	
    capture.release()
    video_writer.release()
    cv2.destroyAllWindows()
