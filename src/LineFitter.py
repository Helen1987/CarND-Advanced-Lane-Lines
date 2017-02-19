import numpy as np


class LineFitter:
    def __init__(self, ym_per_pix, xm_per_pix):
        # Define conversions in x and y from pixels space to meters
        self.ym_per_pix = ym_per_pix # meters per pixel in y dimension
        self.xm_per_pix = xm_per_pix # meters per pixel in x dimension

    def calculate_curvature(self, unscaled_y_eval, unscaled_left_fit, unscaled_right_fit):
        scaled_y = y_values * self.ym_per_pix
        left_fit = np.polyfit(scaled_y, left_x * self.xm_per_pix, 2)
        right_fit = np.polyfit(scaled_y, right_x * self.xm_per_pix, 2)

        left_curverad = ((1+(2*left_fit[0]*y_eval+left_fit[1])**2)**1.5)/np.absolute(2*left_fit[0])
        right_curverad = ((1+(2*right_fit[0]*y_eval+right_fit[1])**2)**1.5)/np.absolute(2*right_fit[0])

        return left_curverad, right_curverad

    def fit_polynomial(self, x_centroids, y_values):
        left_x = np.array(x_centroids)[:, 0]
        right_x = np.array(x_centroids)[:, 1]
        left_fit = np.polyfit(y_values, left_x, 2)
        right_fit = np.polyfit(y_values, right_x, 2)

        # Define y-value where we want radius of curvature
        # I'll choose the maximum y-value, corresponding to the bottom of the image
        y_eval = np.max(y_values)
        return left_fit, right_fit

    def get_plot_coordinates(self, image):
        image_height = image.shape[0]
        ploty = np.linspace(0, image_height - 1, image_height)
        left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
        right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]
        return ploty, left_fitx, right_fitx
