import logging
import cv2

# ============================================================================
class VehicleCounter(object):
    def __init__(self, shape, divider):
        self.log = logging.getLogger("vehicle_counter")

        self.height, self.width = shape
        self.divider = divider

        self.vehicle_count = 0


    def update_count(self, matche, output_image = None):
        contour, centroid = matche
        x, y, w, h = contour
        cx,cy = centroid

        if cx < self.width and cy < self.divider:
            self.vehicle_count += 1
            self.log.debug("Updating count using %d matches...", self.vehicle_count)
# ============================================================================