import numpy as np
import cv2
from PIL import Image
import sys
import os

# cap = cv2.VideoCapture('slow.flv')

# get 2 pics from command line
numArgs = sys.argv.__len__()
if numArgs != 4:
    print("Wrong number of command line arguments. LucasKanade.py expects 3 command line args")
    print("Usage: python3 LucasKanade.py /path/to/pic1 /path/to/pic2 downsizeFactor")
    exit(1)

images = []
imagesLowRes = []
downscaleFactor = int(sys.argv[3])
for x in range(1, numArgs-1):
    filePath = sys.argv[x]
    # get the file name for saving later
    # file = os.path.basename(filePath)
    image = cv2.imread(filePath)
    height, width, channels = image.shape
    lowRes = cv2.resize(src=image, dsize=(int(width/downscaleFactor), int(height/downscaleFactor)), interpolation=cv2.INTER_AREA)
    lowRes = cv2.resize(src=lowRes, dsize=(int(width), int(height)), interpolation=cv2.INTER_AREA)

    imagesLowRes.append(lowRes)
    # images.append(image)


# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 100,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Create some random colors
color = np.random.randint(0,255,(100,3))

# Take first frame and find corners in it
old_frame = imagesLowRes[0]
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)

# Create a mask image for drawing purposes
lines = np.zeros_like(old_frame)
circles = np.zeros_like(old_frame)



radius = 2
#masks = [];
frame = None
for im in imagesLowRes:
    # get the nex frame
    frame = im
    # make frame grey scale
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # calculate optical flow
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

    # Select good points
    good_new = p1[st==1]
    good_old = p0[st==1]

    # draw the tracks
    for i,(new,old) in enumerate(zip(good_new,good_old)):
        a,b = new.ravel()
        c,d = old.ravel()
        lines = cv2.line(lines, (a,b),(c,d), color[i].tolist(), 2)
        circles = cv2.circle(circles,(a,b),radius,color[i].tolist(),-1)
    #img = cv2.add(frame,mask)

    radius += 1
    #cv2.imshow('frame',img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

    # Now update the previous frame and previous points
    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1,1,2)


# for mask in masks:
#    cv2.add(frame,mask)
img = cv2.add(frame,lines)
img = cv2.add(img,circles)
# scale up for presentation
#lowRes = cv2.resize(src=img, dsize=(int(width), int(height)), interpolation=cv2.INTER_CUBIC)
cv2.imwrite('flow.jpg',img)
cv2.imshow('frame',frame)
input("Press Enter to continue...")
# cv2.destroyAllWindows()
