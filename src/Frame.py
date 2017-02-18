import cv2
import numpy as np

import Line


class Frame:
    def __init(self, img):
        # calibrate the camera
        self.img = img
        self.result_img = None

    def get_line(self):
        return Line()

    def _undistort_image(self, mtx, dist):
        return cv2.undistort(self.img, mtx, dist, None, mtx)

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
        binary[((s_channel >= s_thresh[0]) & (s_channel <= s_thresh[1]))
                | ((v_channel >= v_thresh[0]) & (v_channel <= v_thresh[1]))
                | ((scaled_sobel > sx_thresh[0]) & (scaled_sobel < sx_thresh[1]))] = 1
        return binary

    def _bird_view_transformation(self, img, s_points, d_points):
        matrix = cv2.getPerspectiveTransform(src.astype(np.float32), dst)
        return cv2.warpPerspective(img, matrix, (img.shape[1], img.shape[0]))

    def _select_lines(self, img):
        histogram = np.sum(img[img.shape[0]/2:, :], axis=0)
        plt.plot(histogram)

    def preprocess_frame(self, mtx, dist, s_points, d_points):
        img = self._undistort_image(selg.img, mtx, dist)
        img = self._get_thresholded_image(img)
        img = self._bird_view_transformation(img, s_points, d_points)

    def draw_line_area(self):
        # Create an image to draw the lines on
        warp_zero = np.zeros_like(warped).astype(np.uint8)
        color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

        # Recast the x and y points into usable format for cv2.fillPoly()
        pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
        pts = np.hstack((pts_left, pts_right))

        # Draw the lane onto the warped blank image
        cv2.fillPoly(color_warp, np.int_([pts]), (0,255, 0))

        # Warp the blank back to original image space using inverse perspective matrix (Minv)
        newwarp = cv2.warpPerspective(color_warp, Minv, (image.shape[1], image.shape[0])) 
        # Combine the result with the original image
        result = cv2.addWeighted(undist, 1, newwarp, 0.3, 0)
        #plt.imshow(result)

    def get_result_image(self):
        return self.result_img