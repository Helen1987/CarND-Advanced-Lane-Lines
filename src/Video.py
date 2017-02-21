import numpy as np
import os
import sys
import cv2
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
        self.last_n_lines = LastNLines(5, 20)
        self.matrix = None
        self.inverse_matrix = None

    def _init_perspective_points(self, width, height):
        top_offset = 110
        bottom_offset = 10
        top_line_offset = 110

        s_points = np.float32([
            (0, height-bottom_offset),
            (width/2-top_line_offset, height/2+top_offset),
            (width/2+top_line_offset, height/2+top_offset),
            (width, height-bottom_offset)])
        
        offset = 100
        d_points = np.float32([
            [offset, height], [offset, 0],
            [width-offset, 0], [width-offset, height]])

        self.matrix = cv2.getPerspectiveTransform(s_points, d_points)
        self.inverse_matrix = cv2.getPerspectiveTransform(d_points, s_points)

    def handle_frame(self, image):
        try:
            current_frame = Frame(image, self.mtx, self.dist)
            bird_view_img = current_frame.preprocess_frame(self.matrix)

            self.last_n_lines.add_new_line(bird_view_img)
            left, right = self.last_n_lines.get_best_fit_lines()

            result = current_frame.draw_line_area(left, right, self.inverse_matrix)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        return result

    def process(self):
        project_video = VideoFileClip(self.path)
        self._init_perspective_points(project_video.size[0], project_video.size[1])
        self.last_n_lines.init(project_video.size[0], project_video.size[1])

        new_video = project_video.fl_image(self.handle_frame)
        output_file_name = os.path.join(self.output_folder, "result_" + self.path)
        new_video.write_videofile(output_file_name, audio=False)
