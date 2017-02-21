**Advanced Lane Finding Project**

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[original_cam]: ./examples/distorted_image.png "Original"
[undistorted_cam]: ./examples/undistort_output.png "Undistorted"
[or_road]: ./test_images/test1.jpg "Original Road"
[und_road]: ./test_images/test1.jpg "Road Transformed"
[roi]: ./examples/test1.jpg "Region of interest"
[wraped]: ./examples/binary_combo_example.jpg "Bird-view image"
[image4]: ./examples/warped_straight_lines.jpg "Warp Example"
[image5]: ./examples/color_fit_lines.jpg "Fit Visual"
[final]: ./examples/example_output.jpg "Resulted output"
[r_track1]: ./output_video/result_project_video.mp4 "Video1"

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points
---
###Writeup / README

####1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  [Here](https://github.com/udacity/CarND-Advanced-Lane-Lines/blob/master/writeup_template.md) is a template writeup for this project you can use as a guide and a starting point.  

You're reading it!
###Camera Calibration

####1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

To calibrate camera I use [IPython notebook](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/research/Calibration.ipynb).

I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. I can find them with `cv2.findChessboardCorners`. The result chessboard is the same chessboard for all images on a plane z=0. So I need to create an array of (x, y) coordinates for expected 9x6 chessboard. Thus, `objp` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  

I then used the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function.  I applied this distortion correction to the test image using the `cv2.undistort()` function and obtained this result: 

![alt text][original_cam]
![alt text][undistorted_cam]

###Pipeline (single images)

####1. Provide an example of a distortion-corrected image.
To demonstrate this step, I will describe how I apply the distortion correction to one of the test images like this one:
![alt text][or_road]
The code of transorming the image into "bird-view" image you can find in my [Frame class](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/src/Frame.py)
####2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.
I used a combination of color and gradient thresholds to generate a binary image (thresholding steps at lines # through # in `another_file.py`).  Here's an example of my output for this step.  (note: this is not actually from one of the test images)

![alt text][und_road]

####3. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

For all frames I use the same source and destination points. I initialize `source_points` and `destination_points` once in `_init_perspective_points` method of [Video class](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/src/Video.py) based on video image size. For region of interest I choose the region you can see on image below.

![alt text][roi]

This resulted in the following source and destination points:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 585, 460      | 320, 0        | 
| 203, 720      | 320, 720      |
| 1127, 720     | 960, 720      |
| 695, 460      | 960, 0        |

Actual transformation happens in `_bird_view_transformation` method of [Frame class](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/src/Frame.py). The function takes as inputs an image, source and destination points. 

On resulted warped image lines are parallel, so my points are correct

![alt text][wraped]

####4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

To identify lane-line pixels I use convolutional slider approach and search based on previous line position. The code you can find in [ConvolutionalSlide class](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/src/ConvolutionalSlider.py). 

Actually, I use convolution to find lines on ther first image or in case when the second approach did not gave sensible results. The logic of choosing the right appoach you can find in [`add_new_line` method](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/src/LastNLines.py#L36) of [LastNLines class](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/src/LastNLines.py). Convolutional approach you can find in [`get_initial_lines` method](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/src/ConvolutionalSlider.py#L62)

When I have the data from previous line I was able to use it to identify the next line in the same region with some margin. You can find the code in [`get_next_line` method](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/src/ConvolutionalSlider.py#L68)

To calculate information about identified line I use [`LineFitter` class](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/src/LineFitter.py). Specifically, in [`fit_line` method](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/src/LineFitter.py#L24) I fit a line into the second order polynomial and returned data which can be used to draw the resulted line.

To fit line better I use different techniques:
1. Removing outliers which deviates too much from the median
2. Weighted averaging of previous lines to remove jittering

![alt text][image5]

####5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

The code you can find in [`calculate_curvature`](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/src/LineFitter.py#L11) method. To scale the result I use data from lectures about the USA road lane line.

####6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

You can find the code in [`draw_line_area` method](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/src/Frame.py#L39).

First of all I draw the region between two line using best fit data. Then I apply `cv2.warpPerspective` on our bird-view image but with a matrix for inverse transformation. In result we get our final image.

![alt text][final]

---

###Pipeline (video)

####1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

![alt text][r_track1]

---

###Discussion

####1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

My first step was to create a basic pipeline. Actually, on the first video I got pretty good result if do not take into consideration cement areas. My next step was to use a technique of lane finding based on previous line. It gave very nice results for the first video and I was able to pass the cement area in a nice way.

Then I had two possible ways to improve my pipeline:
1. To improve the way to identify line pixel
2. To use some math techniques and sanity checks for identified pixels

I started from the second part since it is easier to test the result when lines are not identified perfectly. When I was satisfied with the result I switched to the first point.

My pipeline is pretty robust, though I doubt it would work at night. I want to remove some const to a config file or calculate them dinamically based on picture size.

