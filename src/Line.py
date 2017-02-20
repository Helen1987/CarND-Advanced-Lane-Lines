import numpy as np


class Line:
    def __init__(self, fit_coeff, x_values, y_values):
        # was the line detected in the last iteration?
        self.detected = False  
        # x values of the last n fits of the line
        self.recent_xfitted = [] 
        #average x values of the fitted line over the last n iterations
        self.best_x = None
        self.best_y = None
        #polynomial coefficients averaged over the last n iterations
        self.best_fit = fit_coeff # so far
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
