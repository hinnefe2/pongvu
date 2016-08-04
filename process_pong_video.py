#!/usr/bin/python

import matplotlib.pyplot as plt
import matplotlib as mpl
import cv2
import numpy as np
import pandas as pd
import imutils
from collections import deque
import os
import subprocess

AWS_ADDRESS = '54.209.52.220'

def process_frame(frame, show=False, hue_low=10, sat_low=140, val_low=200, hue_hi=35, sat_hi=230, val_hi=255):
    """Process a frame of video and extract the x and y position
    of the center of the ping pong ball, if present
    
    Args:
        frame(np.array): the frame to be processed, as an array of BGR tuples
        
    Returns:
        center(tuple): a tuple containing the x and y position of the ball"""
    
    orangeLower = (hue_low, sat_low, val_low)
    orangeUpper = (hue_hi, sat_hi, val_hi)

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "orange", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, orangeLower, orangeUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    center = (None, None)
    
    # only proceed if at least one contour was found
    if len(contours) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        biggest_contour = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(biggest_contour)
        M = cv2.moments(biggest_contour)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
    if show:
        # only proceed if the radius meets a minimum size
        if radius > 1:
            # draw the circle and centroid on the frame,
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            print(radius)

        #plt.imshow(mask)
        plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
    return center


def process_video(video):
    """Process a video and extract the ball position during each frame
    and the corresponding timestamp
    
    Args:
        video(cv2.VideoCapture): the video to be processed
        
    Returns:
        positions(pandas.DataFrame): a dataframe containing frame timestamp, ball x position, 
                                     and ball y position"""
    
    data = []
    
    while True:
        
        # read the timestamp in msec of the current frame
        timestamp_msec = video.get(0)
        
        # read the current frame
        read_success, frame = video.read()
        
        if not read_success:
            break
            
        # process the frame and save the data
        (ball_x, ball_y) = process_frame(frame)
        
        data.append([timestamp_msec, ball_x, ball_y])
        
    return pd.DataFrame(data, columns=['timestamp_msec', 'ball_x', 'ball_y'])


if __name__ == '__main__':

    pongvu_path = '/home/ubuntu/pongvu/'

    # list all files in the uploads directory
    files_to_process = os.listdir(os.path.join(pongvu_path, 'uploads')

    # process the video files into dataframes
    for filename in files_to_process:

        df = process_video(filename)

        # save the dataframe to a csv
        csv_filename = filename.rstrip('.h264') + '.csv'
        df.to_csv(csv_filename)

        # git add / commit / push the csv file
        bash_cmd = "git add {}".format(csv_filename)
        subprocess.call(bash_cmd)
        bash_cmd = "git commit -m 'adding {}'".format(csv_filename)
        subprocess.call(bash_cmd)
        bash_cmd = "git push origin master"
        subprocess.call(bash_cmd)

        # move the video file out of the uploads folder
        bash_cmd = "mv {} {}".format(
            os.path.join(pongvu_path, 'uploads', filename),
            os.path.join(pongvu_path, 'processed', filename))
        subprocess.call(bash_cmd)
