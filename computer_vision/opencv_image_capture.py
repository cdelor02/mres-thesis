## Save an image
import numpy as np
import argparse
import cv2

parser = argparse.ArgumentParser(description='OpenCV frame saving script')
parser.add_argument('filename', type=str, help='name of destination image \
                                                file (without filetype suffix)')
args = parser.parse_args()
filename = args.filename

# Create a VideoCapture object
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if (cap.isOpened() == False): 
  print("Unable to read camera feed")

# Default resolutions of the frame are obtained.The default resolutions are system dependent.
# We convert the resolutions from float to integer.
frame_width  = int(cap.get(3))
frame_height = int(cap.get(4))
count = 0

print("Ready")

while(True):
    ret, frame = cap.read()

    # Display the resulting frame    
    cv2.imshow('frame', frame)

    # Press Q on keyboard to stop recording
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    elif cv2.waitKey(1) & 0xFF == ord('c'):
        cv2.imwrite(filename + "_%d.jpg" % count, frame)
        print("Captured", count)

    count += 1
  

# When everything done, release the video capture and video write objects
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
