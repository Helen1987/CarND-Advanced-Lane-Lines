import numpy as np
import os
from moviepy.editor import VideoFileClip

from .Frame import Frame
from .LastNLines import LastNLines


class Video:
    def __init__(self, path, output_folder,  mtx, dist):
        # calibrate the camera
        self.mtx = mtx
        self.dist = dist
        self.path = path
        self.output_folder = os.path.join(os.getcwd(), output_folder)
        self.last_n_lines = LastNLines(5)
        self.source_points = None
        self.destination_points = None

    def _init_perspective_points(self, size):
        width = size[0]
        height = size[1]

        top_offset = 110
        bottom_offset = 10
        top_line_offset = 110

        self.source_points = np.float32([
            (0, height-bottom_offset),
            (width/2-top_line_offset, height/2+top_offset),
            (width/2+top_line_offset, height/2+top_offset),
            (width, height-bottom_offset)])
        
        offset = 100
        self.destination_points = np.float32([
            [offset, height], [offset, 0],
            [width-offset, 0], [width-offset, height]])

    def handle_frame(self, image):
        # get image frame
        current_frame = Frame(image, self.mtx, self.dist)
        current_frame.preprocess_frame(self.source_points, self.destination_points)
        # do perspective transformation

        self.last_n_lines.add_new_line(current_frame.bird_view_img)
        left, right = self.last_n_lines.get_best_fit_lines()

        return current_frame.draw_line_area(left, right, self.source_points, self.destination_points)

    def process(self):
        project_video = VideoFileClip(self.path)
        self._init_perspective_points(project_video.size)

        new_video = project_video.fl_image(self.handle_frame)
        output_file_name = os.path.join(self.output_folder, "result_" + self.path)
        new_video.write_videofile(output_file_name, audio=False)
