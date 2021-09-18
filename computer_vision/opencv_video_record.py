import numpy as np
import argparse
import cv2

print('OpenCV video recording script')

parser = argparse.ArgumentParser(description='OpenCV video recording script. \
                                              Please include the filename \
                                              with the filetype included \
                                              (i.e .mp4)')
parser.add_argument('filename', type=str, help='name of destination video file')
args      = parser.parse_args()
filename  = args.filename
directory = "opencv_videos" # hardcoded for now

# Create a VideoCapture object
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if (cap.isOpened() == False): 
  print("Unable to read camera feed")

# Default resolutions of the frame are obtained.The default resolutions are system dependent.
# We convert the resolutions from float to integer.
frame_width  = int(cap.get(3))
frame_height = int(cap.get(4))

# Define the codec and create VideoWriter object. The output is 'filename'.
out = cv2.VideoWriter("./" + directory + "/" + filename,
                      cv2.VideoWriter_fourcc(*'mp4v'), #'M','J','P','G'), 
                      40, (frame_width, frame_height))

print("Commencing recording...")

while(True):
  ret, frame = cap.read()

  if ret == True: 
    
    # Write the frame into the file 'filename'
    out.write(frame)

    # Display the resulting frame    
    cv2.imshow('frame',frame)

    # Press Q on keyboard to stop recording
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  # Break the loop
  else:
    break  

# When everything done, release the video capture and video write objects
cap.release()
out.release()

# Closes all the frames
cv2.destroyAllWindows()
