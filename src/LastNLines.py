import numpy as np
from collections import deque

from .ConvolutionalSlider import ConvolutionalSlider
from .LineFitter import LineFitter
from .Line import Line


class LastNLines:
    def __init__(self, lines_count, max_std):
        self.n = lines_count
        self.MAX_STD = 50
        self.right_lines = deque([])
        self.left_lines = deque([])
        self.slider = ConvolutionalSlider(50, 80, 170, 50)
        self.fitter = None
        self.MIN_LINES_DISTANCE = 0
        self.is_error_line = False
        self.errors_in_a_raw = 0
        self.CRITICAL_ERRORS_COUNT = 20
        self.roots_limit = None

    def init(self, width, height):
        self.fitter = LineFitter(height, 30 / 720, 3.7 / 900)
        self.MIN_LINES_DISTANCE = int(width / 1.7) # diff between lines can't be less
        self.roots_limit = [-height, height]

    def passed_sanity_check(self, left, right):
        diff = np.median(right[0])-np.median(left[0])
        if not((diff > self.MIN_LINES_DISTANCE) and (diff < self.MIN_LINES_DISTANCE + 250)):
            return False
        # check if line intersect
        left_fit = self.fitter.fit_line(left[0], left[1])
        right_fit = self.fitter.fit_line(right[0], right[1])
        coeff = right_fit - left_fit
        roots = np.roots(coeff)
        if ((roots[0] > self.roots_limit[0]) and (roots[0] < self.roots_limit[1])) or ((roots[1] > self.roots_limit[0]) and (roots[1] < self.roots_limit[1])):
            return False
        return True

    def get_best_line_fit(self, x, y, old_lines):
        percentage_coef = 0.9/self.n
        current_coef = percentage_coef

        all_x = x[:]
        all_y = y[:]
        for line in old_lines:
            data_to_take = int(current_coef*len(line.best_x))
            choice = np.random.choice(len(line.best_x), data_to_take)

            all_x = np.append(all_x, line.best_x[choice])
            all_y = np.append(all_y, line.best_y[choice])

            current_coef += percentage_coef

        assert current_coef < 1
        return self.fitter.get_line_data(all_x, all_y)

    def create_line(self, line_data, old_lines):
        line_fit = self.fitter.fit_line(line_data[0], line_data[1])
        x_original, y_original = ConvolutionalSlider.get_filtered_line(
            line_fit, line_data[0], np.array(line_data[1]), self.MAX_STD)

        line_fit, plot_x, plot_y = self.fitter.get_line_data(x_original, y_original)
        best_fit, best_x, best_y = self.get_best_line_fit(plot_x, plot_y, old_lines)
        line = Line(
            line_fit, plot_x, plot_y, best_fit, best_x, best_y,
            self.is_error_line, self.errors_in_a_raw > self.CRITICAL_ERRORS_COUNT)
        line.radius_of_curvature = self.fitter.calculate_curvature(best_x, best_y)
        return line

    def add_new_line(self, image):
        self.is_error_line = 0
        if len(self.left_lines) > 0:
            prev_left_line, prev_right_line = self.get_best_fit_lines()
            left_line_data, right_line_data = self.slider.get_next_lines(
                image, prev_left_line.best_fit, prev_right_line.best_fit)
            if not(self.passed_sanity_check(left_line_data, right_line_data)):
                left_line_data, right_line_data = self.slider.get_initial_lines(image)
                if not(self.passed_sanity_check(left_line_data, right_line_data)):
                    left_line_data = (prev_left_line.best_x, prev_left_line.best_y)
                    right_line_data = (prev_right_line.best_x, prev_right_line.best_y)
                    self.errors_in_a_raw += 1
            else:
                self.errors_in_a_raw = 0
        else:
            left_line_data, right_line_data = self.slider.get_initial_lines(image)

        left_line = self.create_line(left_line_data, self.left_lines)
        right_line = self.create_line(right_line_data, self.right_lines)

        self.left_lines.append(left_line)
        if len(self.left_lines) >= self.n:
            self.left_lines.popleft()
        self.right_lines.append(right_line)
        if len(self.right_lines) >= self.n:
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

