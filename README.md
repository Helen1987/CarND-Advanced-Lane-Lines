## Advanced Lane Finding
[![Udacity - Self-Driving Car NanoDegree](https://s3.amazonaws.com/udacity-sdc/github/shield-carnd.svg)](http://www.udacity.com/drive)

The Project
---

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

My project include files and folders:
* [test_images](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/tree/master/test_images) contains images on which my pipeline was tested to create satisfied results
* [src](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/tree/master/src) contains source code of my pipeline
* [camera_cal](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/tree/master/camera_cal) contains images for camera calibration
* [research](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/tree/master/research) contains jupyter notebooks which I use to build my pipeline
* [process_video.py](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/process_video.py) is used to start the video processing
* [dist_pickle](https://github.com/Helen1987/CarND-Advanced-Lane-Lines/blob/master/dist_pickle.p) is a pickle which contains camera calibration information (generated in notebook)

To start video processing you have to run following command:

`python process_video.py "video_file.mp4" "output_video"`

As a result you will get a video with name *result_video_file.mp4* in *output_video* folder
