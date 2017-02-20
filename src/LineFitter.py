import numpy as np

from .Line import Line


class LineFitter:
    def __init__(self, ym_per_pix, xm_per_pix):
        # Define conversions in x and y from pixels space to meters
        self.ym_per_pix = ym_per_pix # meters per pixel in y dimension
        self.xm_per_pix = xm_per_pix # meters per pixel in x dimension

    def calculate_curvature(self, unscaled_y_values, unscaled_left_fit, unscaled_right_fit):
        scaled_y = unscaled_y_values * self.ym_per_pix
        # Define y-value where we want radius of curvature
        # I'll choose the maximum y-value, corresponding to the bottom of the image
        y_eval = np.max(scaled_y)
        left_fit = np.polyfit(scaled_y, unscaled_left_fit*self.xm_per_pix, 2)
        right_fit = np.polyfit(scaled_y, unscaled_right_fit*self.xm_per_pix, 2)

        left_curverad = ((1+(2*left_fit[0]*y_eval+left_fit[1])**2)**1.5)/np.absolute(2*left_fit[0])
        right_curverad = ((1+(2*right_fit[0]*y_eval+right_fit[1])**2)**1.5)/np.absolute(2*right_fit[0])

        return left_curverad, right_curverad

    def get_plot_coordinates(self, image_height, line_fit):
        plot_y = np.linspace(0, image_height - 1, image_height)
        plot_x = line_fit[0]*plot_y**2+line_fit[1]*plot_y+line_fit[2]
        return plot_x, plot_y

    def get_line(self, image_height, x_left, y_left, x_right, y_right):
        left_fit = np.polyfit(y_left, x_left, 2)
        right_fit = np.polyfit(y_right, x_right, 2)

        left_x, left_y = self.get_plot_coordinates(image_height, left_fit)
        left_line = Line(left_fit, left_x, left_y)

        right_x, right_y = self.get_plot_coordinates(image_height, right_fit)
        right_line = Line(right_fit, right_x, right_y)
        return left_line, right_line
