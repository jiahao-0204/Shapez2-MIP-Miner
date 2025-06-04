"""
The algorithm applies a simple non‑maximum suppression via ``cv2.groupRectangles`` to merge overlapping detections.
"""

import cv2
from skimage.feature import peak_local_max





path = "images/test.jpg"
img_bgr = cv2.imread(path)
if img_bgr is None:
    raise FileNotFoundError(f"Unable to load image: {path}")

roi = cv2.selectROI("Select template", img_bgr, fromCenter=False, showCrosshair=True)
x, y, w, h = roi
template_bgr = img_bgr[y : y + h, x : x + w].copy()

# Step 2: convert to grayscale for correlation
img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
template_gray = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2GRAY)

# Step 3: locate matches
result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)

cv2.imshow("Select template", result)
cv2.waitKey(0)



# find local peaks
template_w = template_gray.shape[1]
template_h = template_gray.shape[0]
min_dist = min(template_w, template_h) // 2  # Minimum distance between peaks

thr_rel = 0.5  # You can adjust this value as needed
loc = peak_local_max(result, min_distance=min_dist, threshold_rel=thr_rel)

# Step 4: draw results
annotated = img_bgr.copy()
for pt in loc:
    x = pt[1] + template_gray.shape[1] // 2
    y = pt[0] + template_gray.shape[0] // 2
    cv2.circle(annotated, (x, y), 10, (0, 0, 255), 2)  # Draw circle at the peak location

# Display
cv2.imshow("Select template", annotated)
cv2.waitKey(0)