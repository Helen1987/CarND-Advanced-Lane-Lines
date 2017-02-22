import cv2
import numpy as np

BLUR_KERNEL = 3


class Frame:
    def __init__(self, img):
        self.img = cv2.undistort(img, Frame.mtx, Frame.dist, None, Frame.mtx)
        self.bird_view_img = None

    @staticmethod
    def init(width, height, mtx, dist):
        top_offset = 100
        bottom_offset = 40
        top_line_offset = 80
        bottom_line_offset = 145

        s_points = np.float32([
            (bottom_line_offset, height - bottom_offset),
            (width / 2 - top_line_offset, height / 2 + top_offset),
            (width / 2 + top_line_offset, height / 2 + top_offset),
            (width - bottom_line_offset, height - bottom_offset)])

        offset = 100
        d_points = np.float32([
            [offset, height], [offset, 0],
            [width - offset, 0], [width - offset, height]])

        Frame.matrix = cv2.getPerspectiveTransform(s_points, d_points)
        Frame.inverse_matrix = cv2.getPerspectiveTransform(d_points, s_points)
        Frame.mtx = mtx
        Frame.dist = dist

    def _equalize(self, img):
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        cl = cv2.equalizeHist(l)

        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    def _get_thresholded_image(self, undistorted, s_thresh=(190, 255), sx_thresh=(30, 80), v_thresh=(200, 240)):
        #hsv = cv2.cvtColor(undistorted, cv2.COLOR_RGB2HSV).astype(np.float)
        #v_channel = hsv[:, :, 2]

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
            #| ((v_channel >= v_thresh[0]) & (v_channel <= v_thresh[1]))
            | ((scaled_sobel > sx_thresh[0]) & (scaled_sobel < sx_thresh[1]))] = 1
        return binary

    def _preprocess_image(self):
        equ = self._equalize(self.img)
        blurred = cv2.GaussianBlur(equ, (BLUR_KERNEL, BLUR_KERNEL), 0)
        return self._get_thresholded_image(blurred)

    def _bird_view_transformation(self, img):
        return cv2.warpPerspective(img, Frame.matrix, (img.shape[1], img.shape[0]))

    def process_frame(self):
        img = self._preprocess_image()
        self.bird_view_img = self._bird_view_transformation(img)
        return self.bird_view_img

    def draw_line_area(self, left_line, right_line):
        # Create an image to draw the lines on
        warp_zero = np.zeros_like(self.bird_view_img).astype(np.uint8)
        color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

        # Recast the x and y points into usable format for cv2.fillPoly()
        pts_left = np.array([np.transpose(
            np.vstack([left_line.best_x, left_line.best_y]))])
        pts_right = np.array([np.flipud(np.transpose(
            np.vstack([right_line.best_x, right_line.best_y])))])
        pts = np.hstack((pts_left, pts_right))

        # Draw the lane onto the warped blank image
        cv2.fillPoly(color_warp, np.int_([pts]), (0, 255, 0))

        #cv2.polylines(color_warp, [left_line.get_line_points()], False, (255, 0, 255), thickness=4)
        #cv2.polylines(color_warp, [right_line.get_line_points()], False, (0, 0, 255), thickness=4)

        # Warp the blank back to original image space using inverse perspective matrix (Minv)

        new_warp = cv2.warpPerspective(color_warp, Frame.inverse_matrix, (self.img.shape[1], self.img.shape[0]))
        # Combine the result with the original image
        result = cv2.addWeighted(self.img, 1, new_warp, 0.3, 0)
        curvature_text = 'Curvature left: ' + str(left_line.radius_of_curvature) + ' m, curvature right: ' + str(right_line.radius_of_curvature) + ' m'
        font = cv2.FONT_HERSHEY_SIMPLEX
        result = cv2.putText(result, curvature_text, (10, 40), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
        distanse = str((1280/2 - (right_line.best_x[0]-left_line.best_x[0])/2)*(3.7/(right_line.best_x[0]-left_line.best_x[0]))) + ' m'
        distanse_text = 'Distance from center is ' + distanse
        return cv2.putText(result, distanse_text, (10, 80), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
