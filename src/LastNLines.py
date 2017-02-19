import numpy as np

import ConvolutionalSlider
import Line




class LastNLine:
    def __init__(self, lines_count):
        self.n = lines_count
        self.slider = ConvolutionalSlider(50, 80, 100)

    def passed_sanity_check(self):
        pass

    def add_new_line(self, image):
        self.slider.find_window_centroids(image, 50, 80)



    def get_new_line(self):
        '''
        If your sanity checks reveal that the lane lines you've detected are problematic for some reason, you can simply assume it was a bad or difficult frame of video, retain the previous positions from the frame prior and step to the next frame to search again. If you lose the lines for several frames in a row, you should probably go back to the blind search method using a histogram and sliding window, or other method, to re-establish your measurement.
        '''

        '''
        Even when everything is working, your line detections will jump around from frame to frame a bit and it can be preferable to smooth over the last n frames 
        of video to obtain a cleaner result. Each time you get a new high-confidence measurement, you can append it to the list of recent measurements and then take
        an average over n past measurements to obtain the lane position you want to draw onto the image.
        '''
        pass

