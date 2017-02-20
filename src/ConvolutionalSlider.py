import numpy as np


class ConvolutionalSlider:
    def __init__(self, window_width, window_height, window_margin):
        self.window_height = window_height
        self.window_width = window_width
        self.window_margin = window_margin
        self.window = np.ones(window_width)  # sliding window for convolutions


    def _find_initial_centroid(self, image):
        # Sum quarter bottom of image to get slice, could use a different ratio
        lower_level = int(3/4*image.shape[0])
        center_border = int(image.shape[1]/2)

        # using np.sum to get the vertical image slice
        l_sum = np.sum(image[lower_level:, :center_border], axis=0)
        l_center = np.argmax(np.convolve(self.window, l_sum)) - self.window_width / 2
        r_sum = np.sum(image[lower_level:, center_border:], axis=0)
        r_center = np.argmax(np.convolve(self.window, r_sum)) - self.window_width / 2 + center_border
        return l_center, r_center

    def _find_next_level_centroids(self, bv_image, centroid, level):
        lower_border = int(bv_image.shape[0] - (level + 1) * self.window_height)

        # convolve the window into the vertical slice of the image
        image_layer = np.sum(bv_image[lower_border:lower_border + self.window_height, :], axis=0)
        conv_signal = np.convolve(self.window, image_layer)

        # Find the best left centroid by using past left center as a reference
        # Use window_width/2 as offset because convolution signal reference
        # is at right side of window, not center of window
        offset = self.window_width/2
        l_min_index = int(max(centroid[0]+offset-self.window_margin, 0))
        l_max_index = int(min(centroid[0] + offset + self.window_margin, bv_image.shape[1]))
        l_center = np.argmax(conv_signal[l_min_index:l_max_index])+l_min_index-offset

        # Find the best right centroid by using past right center as a reference
        r_min_index = int(max(centroid[1]+offset-self.window_margin, 0))
        r_max_index = int(min(centroid[1] + offset + self.window_margin, bv_image.shape[1]))
        r_center = np.argmax(conv_signal[r_min_index:r_max_index])+r_min_index-offset
        return l_center, r_center

    def _find_window_centroids(self, bv_image):
        x_centroids = []  # (left, right) window centroid positions per level
        y_values = []
        image_height = bv_image.shape[0]

        # first find the two starting positions for the left and right lane
        centroid = self._find_initial_centroid(bv_image)
        x_centroids.append(centroid)
        y_values.append(image_height-int(self.window_height/2))

        # go through each layer looking for max pixel locations
        levels_count = int(image_height/self.window_height)
        for level in range(1, levels_count):
            centroid = self._find_next_level_centroids(bv_image, centroid, level)
            x_centroids.append(centroid)
            y_values.append(int(image_height-(level+0.5)*self.window_height))
        return x_centroids, y_values

    def get_initial_lines(self, bv_image):
        x_centroids, y_values = self._find_window_centroids(bv_image)
        left_x = np.array(x_centroids)[:, 0]
        right_x = np.array(x_centroids)[:, 1]
        return (left_x, y_values), (right_x, y_values)
        #return self.fitter.get_line(image_height, left_x, y_values, right_x, y_values)

    def get_next_line(self, bv_warped, left_fit, right_fit):
        non_zero = bv_warped.nonzero()
        non_zero_y = np.array(non_zero[0])
        non_zero_x = np.array(non_zero[1])
        # tricky part with x and y swaped
        left_lane_inds = (
            (non_zero_x > (left_fit[0]*(non_zero_y**2)+left_fit[1]*non_zero_y+left_fit[2]-self.window_margin))
            & (non_zero_x < (left_fit[0]*(non_zero_y**2)+left_fit[1]*non_zero_y+left_fit[2]+self.window_margin)))
        right_lane_inds = (
            (non_zero_x > (right_fit[0]*(non_zero_y**2)+right_fit[1]*non_zero_y+right_fit[2]-self.window_margin))
            & (non_zero_x < (right_fit[0]*(non_zero_y**2)+right_fit[1]*non_zero_y+right_fit[2]+self.window_margin)))

        # Again, extract left and right line pixel positions
        left_x = non_zero_x[left_lane_inds]
        left_y = non_zero_y[left_lane_inds]
        right_x = non_zero_x[right_lane_inds]
        right_y = non_zero_y[right_lane_inds]
        return (left_x, left_y), (right_x, right_y)

        #return self.fitter.get_line(image_height, left_data[0], left_data[1], right_data[0], right_data[1])
