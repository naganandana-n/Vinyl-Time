import cv2
import numpy as np

# Load the image
image = cv2.imread("groove_finder_test_images/test_vinyl_3.webp")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 🔹 Step 1: Apply Canny Edge Detection
edges = cv2.Canny(gray, 50, 150)

# 🔹 Step 2: Find All Contours (Continuous Edges)
contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

# 🔹 Step 3: Sort Contours by Length (Descending Order)
contours = sorted(contours, key=lambda c: len(c), reverse=True)

# 🔹 Step 4: Select the Top N Longest Continuous Edges
N = 20  # Change this value to keep more or fewer edges
top_contours = contours[:N]

# 🔹 Step 5: Create a Blank Image to Display Only the Selected Edges
filtered_edges = np.zeros_like(edges)
cv2.drawContours(filtered_edges, top_contours, -1, 255, 1)  # Draw the selected edges

# 🔹 Step 6: Detect Circular Shapes (Full & Partial) from the Filtered Edges
circle_contours = []
for cnt in top_contours:
    perimeter = cv2.arcLength(cnt, True)
    area = cv2.contourArea(cnt)

    if perimeter == 0:
        continue  # Avoid division by zero

    circularity = 4 * np.pi * (area / (perimeter ** 2))  # Closer to 1 = more circular
    x, y, w, h = cv2.boundingRect(cnt)
    aspect_ratio = float(w) / h  # Should be close to 1 for circles
    convexity = cv2.isContourConvex(cnt)  # Checks if contour is fully convex

    # 🔹 Allow full & partial circles: Relax circularity & allow non-convex contours
    if 0.8 < aspect_ratio < 1.2 and circularity > 0.01:  # Loosened constraints
        circle_contours.append(cnt)

# 🔹 Step 7: Draw Only the Detected Full & Partial Circular Figures
output = cv2.cvtColor(filtered_edges, cv2.COLOR_GRAY2BGR)
cv2.drawContours(output, circle_contours, -1, (0, 255, 0), 2)  # Green for detected circles

# Show the final processed images
cv2.imshow(f"Top {N} Longest Continuous Edges", filtered_edges)
cv2.imshow("Detected Circular Figures (Full & Partial)", output)
cv2.waitKey(0)
cv2.destroyAllWindows()