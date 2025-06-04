from pathlib import Path
import cv2 
from skimage.feature import peak_local_max


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
IMAGE_PATH = Path("images/input.jpg")  # Path to the image file
WINDOW_NAME = "Image"                 # OpenCV window title
PEAK_THRESHOLD_REL = 0.5              # Relative threshold for peak detection

# -----------------------------------------------------------------------------
# validate input
# -----------------------------------------------------------------------------
if not IMAGE_PATH.exists():
    raise FileNotFoundError(f"Unable to load image: {IMAGE_PATH}")

img_bgr = cv2.imread(str(IMAGE_PATH))
if img_bgr is None:
    raise FileNotFoundError(f"cv2.imread failed: {IMAGE_PATH}")

# -----------------------------------------------------------------------------
# Algorithm variables
# -----------------------------------------------------------------------------

# left click
x0: int = 0
y0: int = 0

# right click
x1: int = 0
y1: int = 0

# template rectangle
x: int = 0
y: int = 0
w: int = 0
h: int = 0

# peaks (template matched locations)
peaks = []

# control flow variables
update_template_matching = False
draw_new_peaks = False
draw_new_clicked_position = False

# -----------------------------------------------------------------------------
# mouse callback and template matching
# -----------------------------------------------------------------------------

# start a window
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

# register mouse callback
def mouse_callback(event: int, x_clicked: int, y_clicked: int, flags: int, param):
    global draw_new_clicked_position
    global update_template_matching
    global x0, y0, x1, y1, x, y, w, h
    global peaks, draw_new_peaks
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # update clicked position
        x0, y0 = x_clicked, y_clicked
        x1, y1 = 0, 0
        draw_new_clicked_position = True
        
    elif event == cv2.EVENT_RBUTTONDOWN:
        
        # update clicked position
        x1, y1 = x_clicked, y_clicked
        draw_new_clicked_position = True
        
        # update template rectangle
        x, y = min(x0, x1), min(y0, y1)
        w, h = abs(x1 - x0), abs(y1 - y0)
                
        # extract template
        template_bgr = img_bgr[y : y + h, x : x + w]

        # template matching
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)

        # find local peaks
        min_dist = min(w, h) // 2
        peaks = peak_local_max(result, min_distance=min_dist, threshold_rel=PEAK_THRESHOLD_REL)
        
        # request update peaks
        draw_new_peaks = True

cv2.setMouseCallback(WINDOW_NAME, mouse_callback)


# -----------------------------------------------------------------------------
# render result
# -----------------------------------------------------------------------------
result = img_bgr.copy() 

while True:    
    # draw new clicked position
    if draw_new_clicked_position:
        draw_new_clicked_position = False
        
        # reset image
        result = img_bgr.copy()
        
        # draw clicked positions
        if x0 is not None and y0 is not None:
            cv2.circle(result, (x0, y0), 5, (255, 0, 0), -1)
        if x1 is not None and y1 is not None:
            cv2.circle(result, (x1, y1), 5, (0, 255, 255), -1)
    
    # draw new peaks
    if draw_new_peaks:
        draw_new_peaks = False
        
        # draw selected rectangle
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)    
        
        # draw peaks
        for (row, col) in peaks:
            cx = col + w // 2
            cy = row + h // 2
            cv2.circle(result, (cx, cy), 10, (0, 0, 255), 2)       
    
    # draw image
    cv2.imshow(WINDOW_NAME, result)

    # quite if 'q' is pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


# -----------------------------------------------------------------------------
# cleanup
# -----------------------------------------------------------------------------
cv2.destroyAllWindows()