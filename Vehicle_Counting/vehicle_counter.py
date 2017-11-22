import logging

# ============================================================================
class VehicleCounter(object):
    def __init__(self, shape, divider):
        self.log = logging.getLogger("vehicle_counter")

        self.height, self.width = shape
        self.divider = divider

        self.vehicle_count = 0


    def update_count(self, matches, output_image = None):
        self.log.debug("Updating count using %d matches...", len(matches))

# ============================================================================