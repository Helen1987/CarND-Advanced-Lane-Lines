import numpy as np


class LineFitter:
    def __init__(self, height, ym_per_pix, xm_per_pix):
        # Define conversions in x and y from pixels space to meters
        self.ym_per_pix = ym_per_pix # meters per pixel in y dimension
        self.xm_per_pix = xm_per_pix # meters per pixel in x dimension
        self.image_height = height

    def calculate_curvature(self, unscaled_x, unscaled_y):
        scaled_y = unscaled_y * self.ym_per_pix
        # Define y-value where we want radius of curvature
        # I'll choose the maximum y-value, corresponding to the bottom of the image
        y_eval = np.max(scaled_y)
        fit = self.fit_line(unscaled_x*self.xm_per_pix, scaled_y)

        return ((1+(2*fit[0]*y_eval+fit[1])**2)**1.5)/np.absolute(2*fit[0])

    def fit_line(self, x, y):
        return np.polyfit(y, x, 2)

    def get_line_data(self, x, y):
        line_fit = self.fit_line(x, y)

        plot_y = np.linspace(0, self.image_height - 1, self.image_height)
        plot_x = line_fit[0] * plot_y ** 2 + line_fit[1] * plot_y + line_fit[2]
        return line_fit, plot_x, plot_y
