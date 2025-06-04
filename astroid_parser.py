# system
from pathlib import Path

# third-party
from skimage.feature import peak_local_max
import numpy as np
import cv2 
import matplotlib.pyplot as plt

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

# todo - refactor this
def peaks_to_simple_coordinate(peaks: np.ndarray, tol: float | None = None) -> np.ndarray:
    # check input
    peaks = np.asarray(peaks, dtype=float)
    if peaks.ndim != 2 or peaks.shape[1] != 2:
        raise ValueError("peaks must be (N, 2) array of (row, col) positions")

    # get x and y coordinates
    ys, xs = peaks[:, 0], peaks[:, 1]

    # ---------------------------------------------------------------------
    # Helper – greedy 1-D clustering into bins separated by > tol_axis
    # ---------------------------------------------------------------------
    def cluster_axis(vals: np.ndarray, tol_axis: float) -> np.ndarray:
        sort_idx = np.argsort(vals)
        sorted_vals = vals[sort_idx]
        labels_sorted = np.empty_like(sorted_vals, dtype=int)
        cluster_centers: list[float] = []

        for i, v in enumerate(sorted_vals):
            # Assign to first existing cluster within tolerance
            for c_idx, c in enumerate(cluster_centers):
                if abs(v - c) <= tol_axis:
                    labels_sorted[i] = c_idx
                    # Running update of cluster centre for stability
                    cluster_centers[c_idx] = (c + v) / 2.0
                    break
            else:  # No break → new cluster
                cluster_centers.append(v)
                labels_sorted[i] = len(cluster_centers) - 1

        # Map to 0, 1, 2, ... in ascending spatial order
        order = np.argsort(cluster_centers)
        remap = {old: new for new, old in enumerate(order)}
        labels_sorted = np.vectorize(remap.get)(labels_sorted)
        # Restore original order of peaks
        labels = np.empty_like(labels_sorted)
        labels[sort_idx] = labels_sorted
        return labels

    # ---------------------------------------------------------------------
    # Helper - Auto-estimate tolerance if not supplied (half median spacing)
    # ---------------------------------------------------------------------
    def auto_tol(v: np.ndarray) -> float:
        diffs = np.diff(np.sort(v))
        diffs = diffs[diffs > 5]  
        return float(np.median(diffs)) / 2
    tol_x = tol if tol is not None else auto_tol(xs)
    tol_y = tol if tol is not None else auto_tol(ys)

    # cluster
    row_idx = cluster_axis(ys, tol_y)
    col_idx = cluster_axis(xs, tol_x)
    return np.column_stack((col_idx, -row_idx))


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
    simple_coordinates = np.empty((0, 2), dtype=float)
    draw_new_peaks = False
    draw_new_clicked_position = False
    def mouse_callback(event: int, x_clicked: int, y_clicked: int, flags: int, param):
        """
        left click: set template position 1
        right click: set template position 2 and perform template matching
        """
        nonlocal x0, y0, x1, y1, x, y, w, h, peaks, simple_coordinates, draw_new_peaks, draw_new_clicked_position
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
            simple_coordinates = peaks_to_simple_coordinate(np.array(peaks), min(w, h) // 2)
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
            
            # draw simple coordinates
            plt.clf()
            if simple_coordinates.size > 0:
                plt.scatter(simple_coordinates[:, 0], simple_coordinates[:, 1], marker='s', c='lightgrey', label='Simple Coordinates')
            xmin = np.min(simple_coordinates[:, 0])
            xmax = np.max(simple_coordinates[:, 0])
            ymin = np.min(simple_coordinates[:, 1])
            ymax = np.max(simple_coordinates[:, 1])
            plt.xticks(np.arange(xmin, xmax + 1, 1))
            plt.yticks(np.arange(ymin, ymax + 1, 1))
            plt.grid(True)
            plt.axis('equal')
            plt.title("Simple Coordinates")
            plt.pause(0.001)  # allow plt to update
                        
        # display result
        cv2.imshow(window_name, result)
                
        # quit on 'q' key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        
    cv2.destroyAllWindows()
    plt.close()
    
    # -------------------------------------------------------------
    # return
    # -------------------------------------------------------------
    return simple_coordinates

if __name__ == "__main__":
    simple_coordinates = astroid_parser(Path("images/input.jpg"), 0.5)
    print(simple_coordinates)