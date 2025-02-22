# opencv test

import cv2
import numpy as np

# Create a blank image
image = np.zeros((500, 500, 3), dtype="uint8")

# Draw a circle in that blank image
cv2.circle(image, (250, 250), 100, (0, 255, 0), 3)

# Show the test image
cv2.imshow("Test Window", image)
cv2.waitKey(0)
cv2.destroyAllWindows()