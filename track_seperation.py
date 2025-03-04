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

# Show the final processed image with only the top N longest edges
cv2.imshow(f"Top {N} Longest Continuous Edges", filtered_edges)
cv2.waitKey(0)
cv2.destroyAllWindows()