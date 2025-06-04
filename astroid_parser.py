# system
from pathlib import Path

# third-party
from skimage.feature import peak_local_max
import numpy as np
import cv2 

def template_matching(img_bgr: np.ndarray, x: int, y: int, w: int, h: int, peak_threshold_rel: float):
    # get template
    template_bgr = img_bgr[y : y + h, x : x + w]
    
    # convert to grayscale
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2GRAY)
    
    # perform template matching
    result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    
    # update peaks
    min_dist = min(w, h) // 2
    peaks = peak_local_max(result, min_distance=min_dist, threshold_rel=peak_threshold_rel)
    
    return peaks

def astroid_parser(image_path: Path, peak_threshold_rel: float = 0.5):
    """
    A simple parser to detect peaks in an image using template matching.
    The user can select a template by clicking and dragging the mouse.
    Peaks are detected based on the template and displayed on the image.
    """
    
    # -------------------------------------------------------------
    # validate input
    # -------------------------------------------------------------
    
    # check path
    if not image_path.exists():
        raise FileNotFoundError(f"Unable to load image: {image_path}")
    
    # read image
    img_bgr = cv2.imread(str(image_path))
    if img_bgr is None:
        raise FileNotFoundError(f"cv2.imread failed: {image_path}")
    
    # -------------------------------------------------------------
    # mouse click to interact and template match
    # -------------------------------------------------------------
        
    # create a window
    window_name = "Astroid Parser"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    
    # define interaction
    x0 = y0 = 0 # left click position
    x1 = y1 = 0 # right click position
    x = y = w = h = 0 # template rectangle position and size
    peaks = [] # peaks detected in the image
    draw_new_peaks = False
    draw_new_clicked_position = False
    def mouse_callback(event: int, x_clicked: int, y_clicked: int, flags: int, param):
        """
        left click: set template position 1
        right click: set template position 2 and perform template matching
        """
        nonlocal x0, y0, x1, y1, x, y, w, h, peaks, draw_new_peaks, draw_new_clicked_position
        if event == cv2.EVENT_LBUTTONDOWN:
            # Update clicked position for left click
            x0, y0 = x_clicked, y_clicked
            x1, y1 = 0, 0
            draw_new_clicked_position = True

        # perform template matching on right click
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Update clicked position for right click
            x1, y1 = x_clicked, y_clicked
            draw_new_clicked_position = True

            # compute template rectangle position and size
            x, y = min(x0, x1), min(y0, y1)
            w, h = abs(x1 - x0), abs(y1 - y0)

            # perform template matching
            peaks = template_matching(img_bgr, x, y, w, h, peak_threshold_rel)
            draw_new_peaks = True
    
    # link interaction
    cv2.setMouseCallback(window_name, mouse_callback)

    # -------------------------------------------------------------
    # render image for inspection
    # -------------------------------------------------------------
    
    result = img_bgr.copy()
    while True:
        # clicked positions
        if draw_new_clicked_position:
            draw_new_clicked_position = False
            
            # reset result image
            result = img_bgr.copy()
            
            # draw new clicked positions
            if x0 is not None and y0 is not None:
                cv2.circle(result, (x0, y0), 5, (255, 0, 0), -1)
            if x1 is not None and y1 is not None:
                cv2.circle(result, (x1, y1), 5, (0, 255, 255), -1)

        # peaks
        if draw_new_peaks:
            draw_new_peaks = False
            
            # draw template rectangle
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # draw peaks
            for (row, col) in peaks:
                cx = col + w // 2
                cy = row + h // 2
                cv2.circle(result, (cx, cy), 10, (0, 0, 255), 2)

        # display result
        cv2.imshow(window_name, result)

        # quit on 'q' key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        
    cv2.destroyAllWindows()
    
    # -------------------------------------------------------------
    # after inspection, return
    # -------------------------------------------------------------
    return peaks
    
if __name__ == "__main__":
    peaks = astroid_parser(Path("images/input.jpg"), 0.5)