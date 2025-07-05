import os
import time
import cv2
from picamera2 import Picamera2

# Setup: resolution 640x480
picam = Picamera2()
picam.configure(picam.create_still_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam.start()

# Get the next available image number
def get_next_image_number():
    i = 1
    while os.path.exists(f"image{i}.jpg"):
        i += 1
    return i

print(" Press '0' in terminal to take a photo. Ctrl+C to exit.")
img_count = get_next_image_number()

try:
    while True:
        key = input("Press 0 to take photo: ")
        if key == '0':
            frame = picam.capture_array()
            filename = f"image{img_count}.jpg"
            cv2.imwrite(filename, frame)
            print(f" Saved {filename}")
            cv2.imshow("Captured Photo", frame)
            cv2.waitKey(3000)  # Show for 3 seconds
            cv2.destroyAllWindows()
            img_count += 1
except KeyboardInterrupt:
    print("\n Exiting.")
    picam.close()