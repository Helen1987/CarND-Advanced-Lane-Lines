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
        bottom_offset = 10
        top_line_offset = 75
        bottom_line_offset = 115

        s_points = np.float32([
            (bottom_line_offset, height - bottom_offset),
            (width / 2 - top_line_offset, height / 2 + top_offset),
            (width / 2 + top_line_offset, height / 2 + top_offset),
            (width - bottom_line_offset, height - bottom_offset)])

        offset = 100
        new_height = height * 10
        d_points = np.float32([
            [offset, new_height], [offset, 0],
            [width - offset, 0], [width - offset, new_height]])

        Frame.matrix = cv2.getPerspectiveTransform(s_points, d_points)
        Frame.inverse_matrix = cv2.getPerspectiveTransform(d_points, s_points)
        Frame.mtx = mtx
        Frame.dist = dist
        Frame.bv_size = (width, new_height)

    def _equalize(self, img):
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)

        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    @staticmethod
    def mag_thresh(img, sobel_kernel=3, mag_thresh=(0, 255)):
        # take the gradient in x and y separately
        sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=sobel_kernel)
        sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=sobel_kernel)
        # calculate the magnitude
        magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)
        # scale to 8-bit (0 - 255) and convert to type = np.uint8
        scaled_sobel = np.uint8(255 * magnitude / np.max(magnitude))
        # create a binary mask where mag thresholds are met
        sobel_binary = np.zeros_like(scaled_sobel)
        sobel_binary[(scaled_sobel > mag_thresh[0]) & (scaled_sobel < mag_thresh[1])] = 1

        return sobel_binary

    @staticmethod
    def dir_threshold(img, sobel_kernel=3, thresh=(0, np.pi / 2)):
        # take the gradient in x and y separately
        sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=sobel_kernel)
        sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=sobel_kernel)

        abs_sobelx = np.absolute(sobelx)
        abs_sobely = np.absolute(sobely)
        # calculate the direction of the gradient
        directions = np.arctan2(abs_sobely, abs_sobelx)
        # create a binary mask where direction thresholds are met
        sobel_binary = np.zeros_like(directions)
        sobel_binary[(directions > thresh[0]) & (directions < thresh[1])] = 1

        return sobel_binary

    @staticmethod
    def get_rgb_threshold_image(undistorted, thresh=(250, 255)):
        r_channel = undistorted[:, :, 0]
        binary = np.zeros_like(r_channel)
        binary[(r_channel >= thresh[0]) & (r_channel <= thresh[1])] = 1

        return binary

    @staticmethod
    def get_hsv_threshold_image(equalized, v_thresh=(170, 255), s_thresh=(70, 135)):
        K_SIZE=7
        hsv = cv2.cvtColor(equalized, cv2.COLOR_RGB2HSV).astype(np.float)
        s_channel = hsv[:, :, 1]
        v_channel = hsv[:, :, 2]

        mag_binary = Frame.mag_thresh(s_channel, sobel_kernel=K_SIZE, mag_thresh=(40, 100))
        dir_binary = Frame.dir_threshold(s_channel, sobel_kernel=K_SIZE, thresh=(0.6, 1.1))

        binary = np.zeros_like(v_channel)
        binary[(
            (mag_binary == 1) & (dir_binary == 1)
            & (s_channel >= s_thresh[0]) & (s_channel <= s_thresh[1]))
            & ((v_channel >= v_thresh[0]) & (v_channel <= v_thresh[1]))] = 1
        return binary

    @staticmethod
    def get_hsl_threshold_image(equalized, s_thresh=(180, 255), l_thresh=(215, 255)):
        K_SIZE = 7
        hls = cv2.cvtColor(equalized, cv2.COLOR_RGB2HLS).astype(np.float)
        l_channel = hls[:, :, 1]
        s_channel = hls[:, :, 2]

        s_mag_binary = Frame.mag_thresh(s_channel, sobel_kernel=K_SIZE, mag_thresh=(20, 100))
        s_dir_binary = Frame.dir_threshold(s_channel, sobel_kernel=K_SIZE, thresh=(0.6, 1.1))

        l_mag_binary = Frame.mag_thresh(l_channel, sobel_kernel=K_SIZE, mag_thresh=(20, 100))
        l_dir_binary = Frame.dir_threshold(l_channel, sobel_kernel=K_SIZE, thresh=(0.6, 1.1))

        sl_binary = np.zeros_like(l_channel)
        sl_binary[(
            (s_mag_binary == 1) & (s_dir_binary == 1)
            & (s_channel >= s_thresh[0]) & (s_channel <= s_thresh[1]))
            | ((l_channel > l_thresh[0]) & (l_channel <= l_thresh[1])
            & (l_mag_binary == 1) & (l_dir_binary == 1))] = 1
        return sl_binary

    def _preprocess_image(self):
        equ = self._equalize(self.img)

        r_binary = Frame.get_rgb_threshold_image(self.img)
        hsl_binary = Frame.get_hsl_threshold_image(equ)
        hsv_binary = Frame.get_hsv_threshold_image(equ)

        binary = np.zeros_like(r_binary)
        binary[(r_binary == 1) | (hsl_binary == 1) | (hsv_binary == 1)] = 1

        return binary

    def _bird_view_transformation(self, img):
        return cv2.warpPerspective(img, Frame.matrix, (Frame.bv_size[0], Frame.bv_size[1]))

    def process_frame(self):
        img = self._preprocess_image()
        self.bird_view_img = self._bird_view_transformation(img)
        return self.bird_view_img

    def draw_line_area(self, left_line, right_line):
        if left_line == None:
            return cv2.putText(self.img, "Error", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        else:
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
            distanse = str(((right_line.best_x[0]+left_line.best_x[0])/2-1280/2)*(3.7/900)) + ' m'
            distanse_text = 'Distance from center is ' + distanse
            return cv2.putText(result, distanse_text, (10, 80), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
