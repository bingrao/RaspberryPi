import logging
import logging.handlers
import os
import time
import sys
import argparse

import cv2

from vehicle_counter import VehicleCounter



# ============================================================================
# Define global  vars
IMAGE_DIR = "images"
IMAGE_FILENAME_FORMAT = IMAGE_DIR + "/frame_%04d.png"

# Time to wait between frames, 0=forever
WAIT_TIME = 1 # 250 # ms

TIME_INTERVAL = 15

# Save the log information into the local file
LOG_TO_FILE = False

# Save intermeidate frame into the disk for later analysis
SAVE_TO_FRAME = False

# Colours for drawing on processed frames
DIVIDER_COLOUR = (255, 255, 0)
BOUNDING_BOX_COLOUR = (255, 0, 0)
CENTROID_COLOUR = (0, 0, 255)

# Identify where the image source come from
IMAGE_SOURCE = None


# Identify if the source come video or streaming
CAPTURE_FROM_VIDEO = False
# ============================================================================

def parse_args():
    log = logging.getLogger("parse_args")
    global LOG_TO_FILE, IMAGE_SOURCE, CAPTURE_FROM_VIDEO, SAVE_TO_FRAME, WAIT_TIME, TIME_INTERVAL

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser(prog='PROG',description="Vehicle Counting based on RaspberryPi 3.0 B+")

    # Create a mutually exclusive group. argparse will make sure that only one of the arguments
    # in the mutually exclusive group was present on the command line:
    group = ap.add_mutually_exclusive_group()
    group.add_argument("-v","--video", help="The path to the video file")
    group.add_argument("-s","--streaming",help="The index of camera that you want to use")
    group.add_argument("-p","--picture", help = "The path to the picture files")

    ap.add_argument("-l","--logFile", help = "Save log into a local file",action="store_true")
    ap.add_argument("-f","--frameSave", help = "Save the intermediate frames",action="store_true")
    ap.add_argument("-i", "--interval", help="The time interval to take a frame from video")

    args = vars(ap.parse_args())

    # Support either video file, or streaming file, or individual frames
    if args.get("video",None) is not None:
        IMAGE_SOURCE = args["video"]
        CAPTURE_FROM_VIDEO = True

    if args.get("streaming",None) is not None:
        IMAGE_SOURCE = int(args["streaming"])
        CAPTURE_FROM_VIDEO = True

    if args.get("picture",None) is not None:
        IMAGE_SOURCE = args["picture"]

    if args.get("interval",None) is not None:
        TIME_INTERVAL = int(args["interval"])

    if args.get("logFile", False):
        LOG_TO_FILE = True

    if args.get("frameSave", False):
        SAVE_TO_FRAME = True

    return ap


def init_logging():
    main_logger = logging.getLogger()

    formatter = logging.Formatter(
        fmt='%(asctime)s.%(msecs)03d %(levelname)-8s [%(name)s] %(message)s'
        , datefmt='%Y-%m-%d %H:%M:%S')

    handler_stream = logging.StreamHandler(sys.stdout)
    handler_stream.setFormatter(formatter)
    main_logger.addHandler(handler_stream)

    if LOG_TO_FILE:
        handler_file = logging.handlers.RotatingFileHandler("debug.log"
            , maxBytes = 2**24
            , backupCount = 10)
        handler_file.setFormatter(formatter)
        main_logger.addHandler(handler_file)

    main_logger.setLevel(logging.DEBUG)

    return main_logger

# ============================================================================

def save_frame(file_name_format, frame_number, frame, label_format):
    log = logging.getLogger("save_frame")
    if SAVE_TO_FRAME:
        file_name = file_name_format % frame_number
        label = label_format % frame_number
        log.debug("Saving %s as '%s'", label, file_name)
        cv2.imwrite(file_name, frame)

# ============================================================================
# Get the central point of a car
def get_centroid(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)

    cx = x + x1
    cy = y + y1

    return (cx, cy)

# ============================================================================

def detect_vehicles(fg_mask):
    log = logging.getLogger("detect_vehicles")

    MIN_CONTOUR_WIDTH = 21
    MIN_CONTOUR_HEIGHT = 21

    # Find the contours of any object in  the image , but not all vehicles
    contours, hierarchy = cv2.findContours(fg_mask
        , cv2.RETR_EXTERNAL
        , cv2.CHAIN_APPROX_SIMPLE)

    log.debug("Found %d vehicle contours.", len(contours))

    # Find valid vehicle contour
    matches = []
    for (i, contour) in enumerate(contours):
        # Get a rectangle of this contour
        (x, y, w, h) = cv2.boundingRect(contour)
        contour_valid = (w >= MIN_CONTOUR_WIDTH) and (h >= MIN_CONTOUR_HEIGHT)

        log.debug("Contour #%d: pos=(x=%d, y=%d) size=(w=%d, h=%d) valid=%s"
            , i, x, y, w, h, contour_valid)

        if not contour_valid:
            continue

        centroid = get_centroid(x, y, w, h)

        matches.append(((x, y, w, h), centroid))

    return matches

# ============================================================================

def filter_mask(fg_mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    # Fill any small holes
    closing = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    # Remove noise
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)

    # Dilate to merge adjacent blobs
    dilation = cv2.dilate(opening, kernel, iterations = 2)

    return dilation

# ============================================================================

def process_frame(frame_number, frame, bg_subtractor, car_counter):
    log = logging.getLogger("process_frame")

    # Create a copy of source frame to draw into
    processed = frame.copy()

    # Draw dividing line -- we count cars as they cross this line.
    cv2.line(processed, (0, car_counter.divider), (frame.shape[1], car_counter.divider), DIVIDER_COLOUR, 1)

    # Remove the background
    fg_mask = bg_subtractor.apply(frame, None, 0.01)
    fg_mask = filter_mask(fg_mask)

    save_frame(IMAGE_DIR + "/mask_%04d.png"
        , frame_number, fg_mask, "foreground mask for frame #%d")

    matches = detect_vehicles(fg_mask)

    log.debug("Found %d valid vehicle contours.", len(matches))
    for (i, match) in enumerate(matches):
        contour, centroid = match

        log.debug("Valid vehicle contour #%d: centroid=%s, bounding_box=%s", i, centroid, contour)

        x, y, w, h = contour

        # Mark the bounding box and the centroid on the processed frame
        # NB: Fixed the off-by one in the bottom right corner
        cv2.rectangle(processed, (x, y), (x + w - 1, y + h - 1), BOUNDING_BOX_COLOUR, 1)
        cv2.circle(processed, centroid, 2, CENTROID_COLOUR, -1)

        if frame_number % TIME_INTERVAL == 1:
            log.debug("Updating vehicle count...")
            car_counter.update_count(match, processed)

        cv2.putText(processed, 'Counting: ' + str(car_counter.vehicle_count),
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    return processed

# ============================================================================

def main():
    log = logging.getLogger("main")

    log.debug("Creating background subtractor...")
    bg_subtractor = cv2.BackgroundSubtractorMOG()

    log.debug("Pre-training the background subtractor...")
    default_bg = cv2.imread(IMAGE_FILENAME_FORMAT % 119)
    bg_subtractor.apply(default_bg, None, 1.0)

    car_counter = None # Will be created after first frame is captured

    # Set up image source
    log.debug("Initializing video capture device #%s...", IMAGE_SOURCE)
    cap = cv2.VideoCapture(IMAGE_SOURCE)

    # Capture every TIME_INTERVAL seconds (here, TIME_INTERVAL = 5)
    #fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)  # Gets the frames per second
    #multiplier = TIME_INTERVAL

    log.debug("Update car counting by every %d ...", TIME_INTERVAL)

    # Check Camera is open or not
    if not cap.isOpened():
        log.debug("The Camera is not open ...")
        cap.open()

    frame_width = cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    frame_height = cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    log.debug("Video capture frame size=(w=%d, h=%d)", frame_width, frame_height)

    log.debug("Starting capture loop...\n")
    frame_number = -1
    while True:
        frame_number += 1
        ret, frame = cap.read()
        if not ret:
            log.error("Frame capture failed, stopping...")
            break

        log.debug("Got frame #%d: shape=%s", frame_number, frame.shape)

        if car_counter is None:
            # We do this here, so that we can initialize with actual frame size
            log.debug("Creating vehicle counter...")
            car_counter = VehicleCounter(frame.shape[:2], frame.shape[0] / 2)

        # Archive raw frames from video to disk for later inspection/testing
        if CAPTURE_FROM_VIDEO:
            save_frame(IMAGE_FILENAME_FORMAT
                , frame_number, frame, "source frame #%d")

        log.debug("Processing frame #%d...", frame_number)
        processed = process_frame(frame_number, frame, bg_subtractor, car_counter)

        save_frame(IMAGE_DIR + "/processed_%04d.png"
            , frame_number, processed, "processed frame #%d")

        cv2.imshow('Source Image', frame)
        cv2.imshow('Processed Image', processed)

        log.debug("Frame #%d processed.\n", frame_number)

        c = cv2.waitKey(WAIT_TIME)
        if c == 27:
            log.debug("ESC detected, stopping...")
            break

    log.debug("Closing video capture device...")
    cap.release()
    cv2.destroyAllWindows()
    log.debug("Done.")

# ============================================================================

if __name__ == "__main__":

    # Parse the arguments from command line
    ap = parse_args()

    # Initial log engine
    log = init_logging()

    if IMAGE_SOURCE is None:
        log.error("Please refer to the following help info...")
        ap.print_help()
        sys.exit(0)

    if not os.path.exists(IMAGE_DIR):
        log.debug("Creating image directory `%s`...", IMAGE_DIR)
        os.makedirs(IMAGE_DIR)

    main()