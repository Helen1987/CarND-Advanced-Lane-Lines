import numpy as np


class Line:
    def __init__(self, fit_coeff, x_values, y_values, best_coeff, x_best, y_best, is_error, is_dangerous):
        if is_error:
            print("was taken previous line")
        if is_dangerous:
            print("too many errors on predicting")
        #average x values of the fitted line over the last n iterations
        self.best_x = x_best
        self.best_y = y_best
        #polynomial coefficients averaged over the last n iterations
        self.best_fit = best_coeff # so far
        #polynomial coefficients for the most recent fit
        self.current_fit = fit_coeff
        #radius of curvature of the line in some units
        self.radius_of_curvature = None 
        #distance in meters of vehicle center from the line
        self.line_base_pos = None 
        #difference in fit coefficients between last and new fits
        self.diffs = np.array([0, 0, 0], dtype='float')
        #x values for detected line pixels
        self.all_x = x_values
        #y values for detected line pixels
        self.all_y = y_values
        self.is_error = is_error
        self.is_dangerous = is_dangerous

    def get_line_points(self):
        return np.stack((self.all_x.astype(np.int32), self.all_y.astype(np.int32)), axis=-1)
