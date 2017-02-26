import numpy as np


class ConvolutionalSlider:
    def __init__(self, window_width, window_height, window_margin, conv_threshold):
        self.window_height = window_height
        self.window_width = window_width
        self.margin = window_margin
        self.small_margin = int(window_margin/2)
        self.window = np.ones(window_width)  # sliding window for convolutions
        self.conv_threshold = conv_threshold

    def _find_initial_centroid(self, image):
        # Sum quarter bottom of image to get slice, could use a different ratio
        lower_level = int(4/5*image.shape[0])
        center_border = int(image.shape[1]/2)

        # using np.sum to get the vertical image slice
        l_sum = np.sum(image[lower_level:, :center_border], axis=0)
        l_center = np.argmax(np.convolve(self.window, l_sum)) - self.window_width / 2
        r_sum = np.sum(image[lower_level:, center_border:], axis=0)
        r_center = np.argmax(np.convolve(self.window, r_sum)) - self.window_width / 2 + center_border
        return l_center, r_center

    def find_initial_line_next_centroids(self, warped, level, prev_x, direction, x0):
        lower_border = int(warped.shape[0] - (level + 1) * self.window_height)
        # convolve the window into the vertical slice of the image
        image_layer = np.sum(warped[lower_border:lower_border + self.window_height, :], axis=0)
        conv_signal = np.convolve(self.window, image_layer)
        # Find the best left centroid by using past left center as a reference
        # Use window_width/2 as offset because convolution signal reference is at right
        # side of window, not center of window
        offset = self.window_width / 2
        x_min_index = int(max(prev_x+offset-(self.margin if direction <= 0 else self.small_margin), 0))
        x_max_index = int(min(prev_x+offset+(self.margin if direction >= 0 else self.small_margin), warped.shape[1]))

        conv = conv_signal[x_min_index:x_max_index]
        # if reached the end of the line
        x_center = np.argmax(conv) + x_min_index - offset
        new_center = x_center if np.max(conv) > self.conv_threshold else prev_x

        angle = abs((level*self.window_height)/(new_center-x0)) if (new_center-x0) != 0 else 11
        if (np.max(conv) <= self.conv_threshold) & (angle < 10) & ((x_min_index == 0) | (x_max_index == warped.shape[1])):
            return None, None, None

        # Add what we found for that layer
        new_y = int(warped.shape[0]-(level+0.5)*self.window_height)
        return new_center, new_y if np.max(conv) > self.conv_threshold else 0, new_center-prev_x

    def get_initial_line_centroids(self, bv_image):
        x_left, x_right = [], []  # window centroid x positions per level
        y_left, y_right = [], []
        direction = 0
        image_height = bv_image.shape[0]
        first_y = image_height - int(self.window_height / 2)

        # first find the two starting positions for the left and right lane
        left, right = self._find_initial_centroid(bv_image)
        x_left.append(left)
        y_left.append(first_y)
        x_right.append(right)
        y_right.append(first_y)

        # go through each layer looking for max pixel locations
        levels_count = int(image_height / self.window_height)
        x = left
        for level in range(1, levels_count):
            x, y, direction = self.find_initial_line_next_centroids(bv_image, level, x, direction, left)
            if y is None:
                break
            x_left.append(x)
            y_left.append(y)

        direction = 0
        x = right
        for level in range(1, levels_count):
            x, y, direction = self.find_initial_line_next_centroids(bv_image, level, x, direction, right)
            if y is None:
                break
            x_right.append(x)
            y_right.append(y)

        return np.array(x_left), np.array(y_left), np.array(x_right), np.array(y_right)

    def get_initial_lines(self, bv_image):
        x_left, y_left, x_right, y_right = self.get_initial_line_centroids(bv_image)

        x_left = x_left[y_left.nonzero()]
        x_right = x_right[y_right.nonzero()]
        y_left = y_left[y_left.nonzero()]
        y_right = y_right[y_right.nonzero()]
        return (x_left, y_left), (x_right, y_right)

    @staticmethod
    def get_filtered_line(fit, x, y, margin):
        line_inds = (
            (x > (fit[0]*(y**2)+fit[1]*y+fit[2]-margin))
            & (x < (fit[0]*(y**2)+fit[1]*y+fit[2]+margin)))
        return x[line_inds], y[line_inds]

    def get_next_lines(self, bv_warped, left_fit, right_fit):
        non_zero = bv_warped.nonzero()
        non_zero_y = np.array(non_zero[0])
        non_zero_x = np.array(non_zero[1])

        left_x, left_y = ConvolutionalSlider.get_filtered_line(
            left_fit, non_zero_x, non_zero_y, self.margin)
        right_x, right_y = ConvolutionalSlider.get_filtered_line(
            right_fit, non_zero_x, non_zero_y, self.margin)

        return (left_x, left_y), (right_x, right_y)


