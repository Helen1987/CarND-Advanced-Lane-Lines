import numpy as np


class Line:
    def __init__(self, fit_coeff):
        # was the line detected in the last iteration?
        self.detected = False  
        # x values of the last n fits of the line
        self.recent_xfitted = [] 
        #average x values of the fitted line over the last n iterations
        self.bestx = None     
        #polynomial coefficients averaged over the last n iterations
        self.best_fit = None  
        #polynomial coefficients for the most recent fit
        self.current_fit = fit_coeff
        #radius of curvature of the line in some units
        self.radius_of_curvature = None 
        #distance in meters of vehicle center from the line
        self.line_base_pos = None 
        #difference in fit coefficients between last and new fits
        self.diffs = np.array([0,0,0], dtype='float') 
        #x values for detected line pixels
        self.allx = None  
        #y values for detected line pixels
        self.ally = None

    # replace with best_fit
    def get_plot_coordinates(self, image_height):
        plot_y = np.linspace(0, image_height - 1, image_height)
        plot_x = self.current_fit[0]*plot_y**2+self.current_fit[1]*plot_y+self.current_fit[2]
        return plot_x, plot_y
