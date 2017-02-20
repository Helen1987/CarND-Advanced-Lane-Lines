import numpy as np
from collections import deque

from .ConvolutionalSlider import ConvolutionalSlider
from .LineFitter import LineFitter
from .Line import Line


class LastNLines:
    def __init__(self, lines_count):
        self.n = lines_count
        self.right_lines = deque([])
        self.left_lines = deque([])
        self.slider = ConvolutionalSlider(50, 80, 100)
        self.fitter = LineFitter(30 / 720, 3.7 / 700)

    def passed_sanity_check(self):
        pass

    def get_best_line_fit(self, x, y, old_lines, image_height):
        all_x = x[:]
        all_y = y[:]
        for line in old_lines:
            all_x = np.append(all_x, line.all_x)
            all_y = np.append(all_y, line.all_y)
        return self.fitter.fit_line(all_x, all_y, image_height)

    def create_line(self, line_data, image_height, old_lines):
        line_fit, plot_x, plot_y = self.fitter.fit_line(line_data[0], line_data[1], image_height)
        best_fit, best_x, best_y = self.get_best_line_fit(plot_x, plot_y, old_lines, image_height)
        return Line(line_fit, plot_x, plot_y, best_fit, best_x, best_y)

    def add_new_line(self, image):
        image_height = image.shape[0]
        if len(self.left_lines) > 0:
            left_line_fit, right_line_fit = self.get_best_fit_lines()
            left_line_data, right_line_data = self.slider.get_next_line(
                image, left_line_fit.best_fit, right_line_fit.best_fit)
            # if line passed_sanity_check == False
            # self.slider.get_lines()
            # if line passed_sanity_check == False
            # self.slider.get_best_fit_lines
        else:
            left_line_data, right_line_data = self.slider.get_initial_lines(image)

        left_line = self.create_line(left_line_data, image_height, self.left_lines)
        right_line = self.create_line(right_line_data, image_height, self.right_lines)

        self.left_lines.append(left_line)
        if len(self.left_lines) > self.n:
            self.left_lines.popleft()
        self.right_lines.append(right_line)
        if len(self.right_lines) > self.n:
            self.right_lines.popleft()

    def get_best_fit_lines(self):
        return self.left_lines[-1], self.right_lines[-1]
        '''
        If your sanity checks reveal that the lane lines you've detected are problematic for some reason, you can simply assume it was a bad or difficult frame of video, retain the previous positions from the frame prior and step to the next frame to search again. If you lose the lines for several frames in a row, you should probably go back to the blind search method using a histogram and sliding window, or other method, to re-establish your measurement.
        '''

        '''
        Even when everything is working, your line detections will jump around from frame to frame a bit and it can be preferable to smooth over the last n frames 
        of video to obtain a cleaner result. Each time you get a new high-confidence measurement, you can append it to the list of recent measurements and then take
        an average over n past measurements to obtain the lane position you want to draw onto the image.
        '''
        pass

