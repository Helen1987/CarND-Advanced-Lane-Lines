import numpy as np

import Frame
import LastNLines


class Video:
    def __init(self, path, mtx, dist):
        # calibrate the camera
        self.mtx = mtx
        self.dist = dist
        self.last_n_lines = LastNLines()
        self.source_points = None
        self.destination_points = None

    def _init_perspective_points(self, img):
        height = new_image.shape[0]
        width = new_image.shape[1]
        top_offset = 110
        bottom_offset = 10
        top_line_offset = 110

        self.source_points = np.float32([
            (0, height-bottom_offset),
            (width/2 - top_line_offset, height/2+top_offset),
            (width/2 + top_line_offset, height/2+top_offset),
            (width, height-bottom_offset)])
        
        offset = 100
        self.destination_points = np.float32([
            [offset, height], [offset, 0],
            [width-offset, 0], [width-offset, height]])

    def start(self):
        # get the first image and initialize
        self._init_perspective_points(img)
        # get image frame
        current_frame = Frame(img)
        current_frame.preprocess_frame(self.mtx, self.dist, self.source_points, self.destination_points)
        # do perspective transformation
        
        new_line = current_frame.get_line()
        if self.last_n_lines.passed_sanity_check(new_line):
            self.last_n_lines.add_new_line(new_line)
        else:
            # start earch from scrach
            pass
        
        result_line = self.last_n_lines.get_new_line()
        current_frame.draw_line_area(result_line)
