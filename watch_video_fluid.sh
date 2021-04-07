#!/bin/sh

#python ./pull_video.py |gst-launch-0.10 fdsrc fd=0 ! h264parse ! autovideosink #|python ./send_joystick.py

python ./pull_video.py |gst-launch-1.0 fdsrc fd=0 ! h264parse ! avdec_h264 ! xvimagesink sync=false |python ./send_joystick.py

