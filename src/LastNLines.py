import numpy as np
from collections import deque

from .ConvolutionalSlider import ConvolutionalSlider
from .LineFitter import LineFitter
from .Line import Line


class LastNLines:
    def __init__(self, lines_count, max_std):
        self.n = lines_count
        self.MAX_STD = max_std
        self.right_lines = deque([])
        self.left_lines = deque([])
        self.slider = ConvolutionalSlider(50, 80, max_std*3)
        self.fitter = None
        self.MIN_LINES_DISTANCE = 0
        self.is_error_line = False
        self.errors_in_a_raw = 0
        self.CRITICAL_ERRORS_COUNT = 10

    def init(self, width, height):
        self.fitter = LineFitter(height, 30 / 720, 3.7 / 700)
        self.MIN_LINES_DISTANCE = int(width / 2.5) # diff between lines can't be less

    def filter_dots(self, x, y):
        #std = np.std(x)
        #if std > self.MAX_STD:
        #    return None, None
        std_ind = np.zeros_like(x, dtype=np.bool)
        for i in range(1, len(x)-1):
            top2 = x[i+1]-x[i]
            bottom2 = x[i]-x[i-1]
            std_ind[i] = (abs(top2) < self.MAX_STD) and (abs(bottom2) < self.MAX_STD) and top2*bottom2 > 0

        # check first and last
        std_ind[0] = (abs(x[1]-x[0]) < self.MAX_STD)
        std_ind[-1] = (abs(x[-1]-x[-2]) < self.MAX_STD)
        #print(std_ind)
        #std_ind = x < np.median(x) + self.MAX_STD
        return x[std_ind], np.array(y)[std_ind]

    def passed_sanity_check(self, left, right):
        if not(np.median(right[0])-np.median(left[0]) > self.MIN_LINES_DISTANCE):
            return False
        return True

    def get_best_line_fit(self, x, y, old_lines):
        all_x = x[:]
        all_y = y[:]
        for line in old_lines:
            all_x = np.append(all_x, line.all_x)
            all_y = np.append(all_y, line.all_y)
        return self.fitter.fit_line(all_x, all_y)

    def create_line(self, line_data, old_lines):
        x_original, y_original = self.filter_dots(line_data[0], line_data[1])
        line_fit, plot_x, plot_y = self.fitter.fit_line(x_original, y_original)
        best_fit, best_x, best_y = self.get_best_line_fit(plot_x, plot_y, old_lines)
        return Line(line_fit, plot_x, plot_y,
                    best_fit, best_x, best_y,
                    self.is_error_line, self.errors_in_a_raw > self.CRITICAL_ERRORS_COUNT)

    def add_new_line(self, image):
        self.is_error_line = 0
        if len(self.left_lines) > 0:
            left_line_fit, right_line_fit = self.get_best_fit_lines()
            left_line_data, right_line_data = self.slider.get_next_line(
                image, left_line_fit.best_fit, right_line_fit.best_fit)
            if not(self.passed_sanity_check(left_line_data, right_line_data)):
                left_line_data, right_line_data = self.slider.get_initial_lines(image)
                if not(self.passed_sanity_check(left_line_data, right_line_data)):
                    left_line_data = (left_line_fit.all_x, left_line_fit.all_y)
                    right_line_data = (right_line_fit.all_x, right_line_data.all_y)
                    self.errors_in_a_raw += 1
            else:
                self.errors_in_a_raw = 0
        else:
            left_line_data, right_line_data = self.slider.get_initial_lines(image)

        left_line = self.create_line(left_line_data, self.left_lines)
        right_line = self.create_line(right_line_data, self.right_lines)

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

