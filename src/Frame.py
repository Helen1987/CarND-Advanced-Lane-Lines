import cv2
import numpy as np


class Frame:
    def __init__(self, img, mtx, dist):
        self.img = cv2.undistort(img, mtx, dist, None, mtx)
        self.bird_view_img = None

    def _get_thresholded_image(self, undistorted, s_thresh=(170, 255), sx_thresh=(20, 100), v_thresh=(200, 240)):
        hsv = cv2.cvtColor(undistorted, cv2.COLOR_RGB2HSV).astype(np.float)
        v_channel = hsv[:, :, 2]

        hls = cv2.cvtColor(undistorted, cv2.COLOR_RGB2HLS).astype(np.float)
        l_channel = hls[:, :, 1]
        s_channel = hls[:, :, 2]

        # Threshold x gradient
        sobel = cv2.Sobel(l_channel, cv2.CV_64F, 1, 0)
        abs_sobel = np.absolute(sobel)
        scaled_sobel = np.uint8(255*abs_sobel/np.max(abs_sobel))
        
        binary = np.zeros_like(s_channel)
        binary[
            ((s_channel >= s_thresh[0]) & (s_channel <= s_thresh[1]))
            | ((v_channel >= v_thresh[0]) & (v_channel <= v_thresh[1]))
            | ((scaled_sobel > sx_thresh[0]) & (scaled_sobel < sx_thresh[1]))] = 1
        return binary

    def _bird_view_transformation(self, img, s_points, d_points):
        matrix = cv2.getPerspectiveTransform(s_points.astype(np.float32), d_points)
        return cv2.warpPerspective(img, matrix, (img.shape[1], img.shape[0]))

    def preprocess_frame(self, s_points, d_points):
        img = self._get_thresholded_image(self.img)
        self.bird_view_img = self._bird_view_transformation(img, s_points, d_points)
        return self.bird_view_img

    def draw_line_area(self, left_line, right_line, s_points, d_points):
        left_fit_x, l_plot_y = left_line.get_plot_coordinates(self.bird_view_img.shape[0])
        right_fit_x, r_plot_y = right_line.get_plot_coordinates(self.bird_view_img.shape[0])
        # Create an image to draw the lines on
        warp_zero = np.zeros_like(self.bird_view_img).astype(np.uint8)
        color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

        # Recast the x and y points into usable format for cv2.fillPoly()
        pts_left = np.array([np.transpose(np.vstack([left_fit_x, l_plot_y]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fit_x, r_plot_y])))])
        pts = np.hstack((pts_left, pts_right))

        # Draw the lane onto the warped blank image
        cv2.fillPoly(color_warp, np.int_([pts]), (0, 255, 0))

        #cv2.polylines(color_warp, [left_line.get_line_points()], False, (255, 0, 255), thickness=40)
        #cv2.polylines(color_warp, [right_line.get_line_points()], False, (0, 0, 255), thickness=40)

        # Warp the blank back to original image space using inverse perspective matrix (Minv)
        matrix = cv2.getPerspectiveTransform(d_points, s_points.astype(np.float32))
        new_warp = cv2.warpPerspective(color_warp, matrix, (self.img.shape[1], self.img.shape[0]))
        # Combine the result with the original image
        return cv2.addWeighted(self.img, 1, new_warp, 0.3, 0)
