import numpy as np


class LineFitter:
    def __init__(self, height, ym_per_pix, xm_per_pix):
        # Define conversions in x and y from pixels space to meters
        self.ym_per_pix = ym_per_pix # meters per pixel in y dimension
        self.xm_per_pix = xm_per_pix # meters per pixel in x dimension
        self.image_height = height

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

    def fit_line(self, x, y):
        return np.polyfit(y, x, 2)

    def get_line_data(self, x, y):
        line_fit = self.fit_line(x, y)

        plot_y = np.linspace(0, self.image_height - 1, self.image_height)
        plot_x = line_fit[0] * plot_y ** 2 + line_fit[1] * plot_y + line_fit[2]
        return line_fit, plot_x, plot_y
