import cv2
import numpy as np

# Load the vinyl image
image = cv2.imread("groove_finder_test_images/test_vinyl_2.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply Gaussian Blur to reduce noise
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# Detect edges
edges = cv2.Canny(blurred, 50, 150)

# Detect circles (assuming vinyl records are circular)
circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1.2, 100,
                           param1=50, param2=30, minRadius=100, maxRadius=500)

# Create a mask to remove non-vinyl areas
mask = np.zeros_like(gray)

if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        center = (i[0], i[1])  # Center of detected vinyl
        radius = i[2]  # Radius of vinyl
        cv2.circle(mask, center, radius, (255, 255, 255), -1)  # Mask out the record

# Apply mask to remove non-vinyl objects
masked_image = cv2.bitwise_and(gray, gray, mask=mask)

# Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) to reduce reflections
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
enhanced = clahe.apply(masked_image)

# Adaptive Thresholding to highlight grooves
thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 11, 2)

# Find contours and draw them (highlighting grooves)
contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(image, contours, -1, (0, 255, 0), 1)

# Show the final detected grooves
cv2.imshow("groove_finder_test5", image)
cv2.waitKey(0)
cv2.destroyAllWindows()