
import cv2
import numpy as np


# Load my test vinyl image
image = cv2.imread("groove_finder_test_images/test_vinyl_2.jpg")

# Convert it to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

'''
# Apply Gaussian blur to reduce noise
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# Use Canny edge detection to highlight grooves (same shit as ANPR)
edges = cv2.Canny(blurred, 50, 150)

# Detect circles using Hough Transform (vinyl grooves gonna be circular)
circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                           param1=50, param2=30, minRadius=50, maxRadius=200)

# Draw detected circles (grooves)
if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        center = (i[0], i[1])  # Center of detected groove
        radius = i[2]  # Radius of the detected groove
        cv2.circle(image, center, radius, (0, 255, 0), 2)  # Draw groove
        cv2.circle(image, center, 2, (0, 0, 255), 3)  # Draw center point

# Show the final (processed) image
cv2.imshow("groove_finder_test1", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''

# the final image was horrible - circles all over the place
# I'm going to use contour detection now:

'''
# Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) to enhance grooves
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
gray = clahe.apply(gray)

# Apply Gaussian blur to reduce noise
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# Adaptive thresholding to improve groove detection
thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 11, 2)

# Morphological opening (removes small white noise)
kernel = np.ones((3,3), np.uint8)
cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

# Detect edges using Canny Edge Detection
edges = cv2.Canny(cleaned, 50, 150)

# Find contours (alternative to circle detection)
contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Draw contours (tracks grooves instead of random circles)
cv2.drawContours(image, contours, -1, (0, 255, 0), 1)

# Show the processed image
cv2.imshow("groove_finder_test2", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''

# better results - but still, there were grooves that weren't detected at all
# i think i need to move towards IR filtering
# since i don't have an IR camera rn, Ill have to simulate an IR image (which can be done with OpenCV)

# Apply a high-pass filter to enhance grooves
high_pass = cv2.subtract(gray, cv2.GaussianBlur(gray, (21, 21), 0))

# Apply thresholding to simulate IR filtering
_, ir_filtered = cv2.threshold(high_pass, 50, 255, cv2.THRESH_BINARY)

# Find edges with Canny
edges = cv2.Canny(ir_filtered, 50, 150)

# Find contours and draw them
contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(image, contours, -1, (0, 255, 0), 1)

# Show the processed image
cv2.imshow("groove_finder_test4", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# i think the issue might be with the test image that I'm using 
# lets try with a more realistic looking image

