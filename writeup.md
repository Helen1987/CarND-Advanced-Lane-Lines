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

[undistorted_cam]: ./examples/undistort_output.png "Original and Undistorted images"
[or_road]: ./test_images/test5.jpg "Original Road"
[und_road]: ./examples/undistorted_test5.jpg "Undistorted Road"
[threshhold1]: ./examples/threshold.jpg "Threshold examples"
[threshhold2]: ./examples/threshold2.jpg "Threshold examples"
[roi]: ./examples/roi_test5.jpg "Region of interest"
[wraped]: ./examples/warped_test5.jpg "Bird-view image"
[line_tuning]: ./examples/line_tuning.jpg "Convolutional Window Tuning"
[final]: ./examples/result_test5.jpg "Resulted output"

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points

###Writeup / README

####1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.

You're reading it!
###Camera Calibration

####1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

To calibrate camera I use [IPython notebook](/research/Calibration.ipynb).

I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. I can find them with `cv2.findChessboardCorners`. The result chessboard is the same chessboard for all images on a plane z=0. So I need to create an array of (x, y) coordinates for expected 9x6 chessboard. Thus, `objp` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  

Then I use the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients with help `cv2.calibrateCamera()` function. I applied this distortion correction to the test image using the `cv2.undistort()` function and obtained this result: 

![alt text][undistorted_cam]

Data usefull for image undistortion I saved into [dist_pickle.p](/dist_pickle.p)

###Pipeline (single images)

To demonstrate the piplein, I will describe how I apply steps to one of the test images like this one:
![alt text][or_road]
The code respponsible for image transforming you can find in my [Frame class](/src/Frame.py)

####1. Provide an example of a distortion-corrected image.

Every time I create a `Frame` object I undistort the image in [constructor](/src/Frame.py#L9).

![alt text][und_road]

####2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.

The whole pipeline of image processing you can find in [`process_frame` method](/src/Frame.py#L72). Firstly, I apply gaussian blur and histogram equalization to prepare image fot further transformation.
Then I use a combination of color and gradient thresholds to generate a binary image in [`_get_thresholded_image` method](/src/Frame.py#L44).  Here's an example of my output for this step:

![alt text][threshhold1]
![alt text][threshhold2]

I tried different techniques but so far combination of Sobel operator over `x` coordinate of L channel from HLS and threholding of S channel gives the best result (HLS image). Though this step is not perfect as we can see from [video2](/output_video/result_challenge_video.mp4) and [video3](/output_video/result_harder_challenge_video.mp4)

####3. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

For all frames I use the same source and destination points. I initialize `source_points` and `destination_points` once in [`init` method](/src/Frame.py#L13) based on video image size. For region of interest I choose the region you can see on image below.

![alt text][roi]

This resulted in the following source and destination points:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 145  680      | 100   720     | 
| 560  460      | 100   0       |
| 720  460      | 1180  0       |
| 1135 680      | 1180  720     |

Actual transformation happens in [`_bird_view_transformation`](/src/Frame.py#L69). On resulted warped image lines are parallel, so my points are correct.

![alt text][wraped]

####4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

To identify lane-line pixels I use convolutional slider approach and search based on previous line position. The code you can find in [ConvolutionalSlide class](/src/ConvolutionalSlider.py). 

Actually, I use convolution to find lines on ther first image or in case when the second approach did not gave sensible results. The logic of choosing the right appoach you can find in [`add_new_line` method](/src/LastNLines.py#L72) of [LastNLines class](/src/LastNLines.py). Convolutional approach you can find in [`get_initial_lines` method](/src/ConvolutionalSlider.py#L62)

When I have the data from previous line I was able to use it to identify the next line in the same region with some margin. You can find the code in [`get_next_lines` method](/src/ConvolutionalSlider.py#L75)

To calculate information about identified line I use [`LineFitter` class](/src/LineFitter.py). Specifically, in [`fit_line` method](/src/LineFitter.py#L20) I fit a line into the second order polynomial and [`get_line_data` method](/src/LineFitter.py#L20) returned line fit and data which can be used to draw the resulted line.

To fit line better I use different techniques:
1. Removing outliers which deviates too much from [the line](/src/ConvolutionalSlider.py#L69)
2. Weighted averaging of previous lines to remove [jittering](/src/LastNLines.py#L41)

On example below you can see identified lines via convolutional approach. Original points and line are displayed on the second image. After removing outliers we can see much better line (the third picture).

![alt text][line_tuning]

####5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

The code to calculate the curvature you can find in [`calculate_curvature`](/src/LineFitter.py#L11) method. To scale the result I use data from lectures about the USA road lane line.

Distance from the line center is calculated in `Frame` class inside [`draw_line_area` method](/src/Frame.py#L77)

####6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

You can find the code in [`draw_line_area` method](/src/Frame.py#L39).

First of all I draw the region between two line using best fit data. Then I apply `cv2.warpPerspective` on our bird-view image but with a matrix for inverse transformation. In result we get our final image.

![alt text][final]

---

###Pipeline (video)

####1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

the first video is good. On the second and the third it is possible to see that lines are not identified correctly, though pipeline is pretty robust.

* [track1](/output_video/result_project_video.mp4 "Video1")
* [track2](/output_video/result_challenge_video.mp4 "Video2")
* [track3](/output_video/result_harder_challenge_video.mp4 "Video3")

---

###Discussion

####1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

My first step was to create a basic pipeline. Actually, on the first video I got pretty good result right away if do not take into consideration cement areas. My next step was to introduce a technique of lane finding based on previous line. It gave very nice results for the first video and I was able to pass the cement area in a nice way.

Then I had two possible ways to improve my pipeline:

1. To improve the way of identifying line pixel
2. Use some math considerations and sanity checks for identified pixels

I started from the second part since it is easier to test the result when lines are not identified perfectly. I introduced some sanity checks (lines do not intersect and far enough from each other). When I was satisfied with the result I switched to the first point.

My pipeline is not robust enough as we can see on the second and the third video. Though histogram normalization improved situation a lot, I still have a lot of issues with line detection. And I doubt I can predict lines at night. I have to improve the thresholding part to make it robust to different conditions.

Though basic pipeline is pretty robust to identify odd images, it is possible to notice that on the third video when the right line is not visible, my pipeline goes crazy. I need to overcome such situations as well.

I want to remove some const to a config file or calculate them dinamically based on picture size.
