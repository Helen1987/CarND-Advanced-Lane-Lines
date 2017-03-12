## Advanced Lane Finding
[![Udacity - Self-Driving Car NanoDegree](https://s3.amazonaws.com/udacity-sdc/github/shield-carnd.svg)](http://www.udacity.com/drive)

The Project
---

[//]: # (Image References)

[result]: ./examples/result_test5.jpg "Final image"

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

![alt text][result]

My project include files and folders:
* [test_images](/test_images) contains images on which my pipeline was tested to create satisfied results
* [src](/src) contains source code of my pipeline
* [camera_cal](/camera_cal) contains images for camera calibration
* [research](/research) contains jupyter notebooks which I use to build my pipeline
* [examples](/examples) contains images for writeup.md
* [writeup.md](/writeup.md) short description of chosen approach
* [process_video.py](/process_video.py) is used to start the video processing
* [dist_pickle.p](/dist_pickle.p) is a pickle which contains camera calibration information (generated in notebook)

To start video processing you have to run following command:

`python process_video.py "video_file.mp4" "output_video"`

As a result you will get a video with name *result_video_file.mp4* in *output_video* folder

## Notes

Project contains two branches:
- [master](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/tree/master) contains code for the first project video
- [advanced](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/tree/advanced) contains code for challenge videos with results:
  - [video1] (https://www.youtube.com/watch?v=1_3l8hsX0Ug)
  - [video2] (https://www.youtube.com/watch?v=6l4mKvmSJVc)
  - [video3] (https://www.youtube.com/watch?v=S2EK5ySOoKk)
