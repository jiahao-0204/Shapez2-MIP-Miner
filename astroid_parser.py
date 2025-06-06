# system
from pathlib import Path
from typing import Optional
from io import BytesIO

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
    
    # invert y and shift up
    row_idx = np.max(row_idx) - row_idx
    
    return np.column_stack((col_idx, row_idx))

def render_template_matching_and_simple_coordinates(img_bgr: np.ndarray, point1: Optional[tuple[int, int]] = None, point2: Optional[tuple[int, int]] = None):
    """
    render the image with marks drawn
    """
    # create a copy of the image
    preview_image = img_bgr.copy()
    
    # draw points
    if point1 is not None:
        cv2.circle(preview_image, point1, 5, (255, 0, 0), -1)
    if point2 is not None:
        cv2.circle(preview_image, point2, 5, (0, 255, 255), -1)
    
    # buffers for rendering
    simple_plot_buffer = None
    
    # draw rectangle and perform template matching if both points are provided
    if point1 is not None and point2 is not None:
        # compute rectangle coordinates
        x = min(point1[0], point2[0])
        y = min(point1[1], point2[1])
        w = abs(point2[0] - point1[0])
        h = abs(point2[1] - point1[1])
        cv2.rectangle(preview_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # ---------------------------------
        # template matching
        # ---------------------------------

        # given both points, perform template matching
        peaks = template_matching(preview_image, x, y, w, h, peak_threshold_rel=0.5)
                
        # draw peaks
        for (row, col) in peaks:
            cx = col + w // 2
            cy = row + h // 2
            cv2.circle(preview_image, (cx, cy), 10, (0, 0, 255), 2)
        
        # ---------------------------------
        # conversion to simple coordinates
        # ---------------------------------
        
        simple_coordinates = peaks_to_simple_coordinate(np.array(peaks), min(w, h) // 2)
        
        # render simple coordinates
        plt.clf()
        if simple_coordinates.size > 0:
            plt.scatter(simple_coordinates[:, 0], simple_coordinates[:, 1], marker='s', c='lightgrey')
            plt.axis('equal')
        simple_plot_buffer = BytesIO()
        plt.savefig(simple_plot_buffer, format='png', bbox_inches='tight')
        plt.close()
        simple_plot_buffer.seek(0)
    
    # Encode preview image
    success, encoded_image = cv2.imencode('.png', preview_image)
    if not success:
        raise RuntimeError("Failed to encode preview image")

    preview_image_buffer = BytesIO(encoded_image.tobytes())

    # return
    return preview_image_buffer, simple_plot_buffer

def astroid_parser(image_path: Path, peak_threshold_rel: float = 0.5):
    """
    A simple parser to detect peaks in an image using template matching.
    The user can select a template by clicking and dragging the mouse.
    Peaks are detected based on the template and displayed on the image.
    """
    
    # -------------------------------------------------------------
    # parser data
    # -------------------------------------------------------------
    point1: Optional[tuple[int, int]] = None
    point2: Optional[tuple[int, int]] = None
    previous_point1: Optional[tuple[int, int]] = None
    previous_point2: Optional[tuple[int, int]] = None
    
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
    # create windows
    # -------------------------------------------------------------        
    
    window_simple_coordinates = "Simple Coordinates Window"
    cv2.namedWindow(window_simple_coordinates, cv2.WINDOW_AUTOSIZE)
    
    window_image = "Image Window"
    cv2.namedWindow(window_image, cv2.WINDOW_AUTOSIZE)    
    
    # -------------------------------------------------------------
    # link callback
    # -------------------------------------------------------------        
    def mouse_callback(event: int, x_clicked: int, y_clicked: int, flags: int, param):
        nonlocal point1, point2
        if event == cv2.EVENT_LBUTTONDOWN:
            point1 = (x_clicked, y_clicked)
            point2 = None  # reset second point
        elif event == cv2.EVENT_RBUTTONDOWN:
            point2 = (x_clicked, y_clicked)
    cv2.setMouseCallback(window_image, mouse_callback)

    # -------------------------------------------------------------
    # render image for inspection
    # -------------------------------------------------------------
    
    while True:
        # update to points
        first_run = (previous_point1 is None and previous_point2 is None)
        update_to_points = (point1 != previous_point1 or point2 != previous_point2)
        
        if update_to_points or first_run:
            previous_point1, previous_point2 = point1, point2
            
            # render image
            preview_image_buffer, simple_plot_buffer = render_template_matching_and_simple_coordinates(img_bgr, point1, point2)
            
            # show image 1
            preview_image = cv2.imdecode(np.frombuffer(preview_image_buffer.getvalue(), np.uint8), cv2.IMREAD_COLOR)   
            cv2.imshow(window_image, preview_image)
            
            # show image 2
            if simple_plot_buffer is not None:
                simple_coordinates_image = cv2.imdecode(np.frombuffer(simple_plot_buffer.getvalue(), np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow(window_simple_coordinates, simple_coordinates_image)
                    
        # quit on 'q' key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        
    # cv2.destroyAllWindows()
    # plt.close()
    
    # -------------------------------------------------------------
    # return
    # -------------------------------------------------------------
    return simple_coordinates

if __name__ == "__main__":
    simple_coordinates = astroid_parser(Path("images/example3.png"), 0.5)
    print(simple_coordinates)