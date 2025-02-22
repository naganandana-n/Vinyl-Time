import cv2
import numpy as np

# Load the vinyl image
image = cv2.imread("groove_finder_test_images/test_vinyl_3.webp")

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Step 1: Detect and Mask Vinyl (Remove Background & Labels)
# Detect circles (vinyl records are circular)
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100,
                           param1=50, param2=30, minRadius=100, maxRadius=500)

# Create a mask to remove non-vinyl areas
mask = np.zeros_like(gray)

if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        center = (i[0], i[1])  # Center of detected vinyl
        radius = i[2]  # Radius of vinyl
        cv2.circle(mask, center, radius, (255, 255, 255), -1)  # Keep only vinyl area

# Apply mask to remove non-vinyl objects
vinyl_only = cv2.bitwise_and(gray, gray, mask=mask)

# 🔹 Step 2: Enhance Groove Contrast 🔹
# Apply Adaptive Histogram Equalization (AHE) to improve contrast
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
contrast_enhanced = clahe.apply(vinyl_only)

# Apply a high-pass filter to remove smooth areas (mimicking IR filtering)
high_pass = cv2.subtract(contrast_enhanced, cv2.GaussianBlur(contrast_enhanced, (21, 21), 0))

# 🔹 Step 3: Thresholding for Groove Detection 🔹
# Apply Adaptive Thresholding to highlight grooves
thresh = cv2.adaptiveThreshold(high_pass, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 11, 2)

# 🔹 Step 4: Find and Filter Contours (Remove Small Noise) 🔹
contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Keep only large contours (likely to be grooves)
filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 50]

# Draw filtered grooves
cv2.drawContours(image, filtered_contours, -1, (0, 255, 0), 1)

# Show the final processed image
cv2.imshow("groove_finder_test6", image)
cv2.waitKey(0)
cv2.destroyAllWindows()