# system
from pathlib import Path
from typing import Optional
from io import BytesIO
import json

# third-party
from skimage.feature import peak_local_max
import numpy as np
import cv2 
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# project
from blueprint_composer import blueprint_to_json, create_empty_blueprint_json, create_miner_json, json_to_blueprint, PREFIX

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
        # if only one value in vals 
        if vals.size <= 1:
            return np.array([0], dtype=int)
        
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
class AstroidParser:
    def __init__(self, img_bgr: np.ndarray, peak_threshold_rel: float = 0.5):
        self.img_bgr = img_bgr
        self.peak_threshold_rel = peak_threshold_rel

        self.point1: Optional[tuple[int, int]] = None
        self.point2: Optional[tuple[int, int]] = None
        
        self.preview_image_buffer = None
        self.preview_image_updated = False
        
        self.simple_coordinate_image_buffer = None
        self.simple_coordinate_image_updated = False
        
        self.simple_coordinates = None

    def add_click(self, x: int, y: int, left: bool):
        if left:
            self.point1 = (x, y)
            # reset point2
            self.point2 = None
        else:
            self.point2 = (x, y)
        
        # update images after click
        self.update_images()

    def update_images(self):
        # reset preview image
        preview_image = self.img_bgr.copy()
        
        # draw clicked points
        if self.point1 is not None:
            cv2.circle(preview_image, self.point1, 5, (255, 0, 0), -1)
        if self.point2 is not None:
            cv2.circle(preview_image, self.point2, 5, (0, 255, 255), -1)

        # proceed if both points are available
        if self.point1 is not None and self.point2 is not None:
            x = min(self.point1[0], self.point2[0])
            y = min(self.point1[1], self.point2[1])
            w = abs(self.point2[0] - self.point1[0])
            h = abs(self.point2[1] - self.point1[1])
            
            # draw rectangle around the selected area
            cv2.rectangle(preview_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # perform template matching to find peaks
            peaks = template_matching(preview_image, x, y, w, h, peak_threshold_rel=self.peak_threshold_rel)
            
            for (row, col) in peaks:
                cx = col + w // 2
                cy = row + h // 2
                cv2.circle(preview_image, (cx, cy), 10, (0, 0, 255), 2)

            # Convert peaks to simplified coordinates
            simple_coordinates = peaks_to_simple_coordinate(np.array(peaks), min(w, h) // 2)

            # plot and store as image buffer
            plt.clf()
            if simple_coordinates.size > 0:
                plt.scatter(simple_coordinates[:, 0], simple_coordinates[:, 1], marker='s', c='lightgrey')
                plt.axis('equal')

            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            plt.close()
            buffer.seek(0)
            self.simple_coordinate_image_buffer = buffer
            self.simple_coordinate_image_updated = True
            
            # store simple coordinates
            self.simple_coordinates = simple_coordinates

        # store preview image as image buffer
        success, encoded_image = cv2.imencode('.png', preview_image)
        if not success:
            raise RuntimeError("Failed to encode preview image")
        preview_image_buffer = BytesIO(encoded_image.tobytes())
        self.preview_image_buffer = preview_image_buffer
        self.preview_image_updated = True

    def request_preview_image(self) -> Optional[BytesIO]:
        # on first request, create the default image
        if not self.preview_image_buffer:
            success, encoded_image = cv2.imencode('.png', self.img_bgr)
            if not success:
                raise RuntimeError("Failed to encode default image")
            self.preview_image_buffer = BytesIO(encoded_image.tobytes())
            self.preview_image_updated = True
        
        if not self.preview_image_updated:
            return None
        else:
            self.preview_image_updated = False
            return self.preview_image_buffer

    def request_simple_coordinates_image(self) -> Optional[BytesIO]:
        if not self.simple_coordinate_image_updated:
            return None
        else:
            self.simple_coordinate_image_updated = False
            return self.simple_coordinate_image_buffer    

    def get_simple_coordinates(self) -> Optional[np.ndarray]:
        return self.simple_coordinates

    def set_threshold(self, peak_threshold_rel: float):
        # set the peak threshold relative value
        self.peak_threshold_rel = min(max(peak_threshold_rel, 0.0), 1.0)
        
        # update images
        self.update_images()
        
        # return the capped threshold
        return self.peak_threshold_rel
    
    def get_threshold(self) -> float:
        return self.peak_threshold_rel
    
def astroid_parser(image_path: Path, peak_threshold_rel: float = 0.5):    
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
    # create parser
    # -------------------------------------------------------------        
    astroid_parser = AstroidParser(img_bgr, peak_threshold_rel=peak_threshold_rel)
    
    # -------------------------------------------------------------
    # create windows
    # -------------------------------------------------------------        
    
    window_simple_coordinates = "Simple Coordinates Window"
    cv2.namedWindow(window_simple_coordinates, cv2.WINDOW_AUTOSIZE)
    
    window_image = "Image Window"
    cv2.namedWindow(window_image, cv2.WINDOW_AUTOSIZE)    
    
    preview_image_buffer = astroid_parser.request_preview_image()
    if preview_image_buffer is not None:
        preview_image = cv2.imdecode(np.frombuffer(preview_image_buffer.getvalue(), np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow(window_image, preview_image)
        
    # -------------------------------------------------------------
    # link callback
    # -------------------------------------------------------------        
    def mouse_callback(event: int, x_clicked: int, y_clicked: int, flags: int, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            point1 = (x_clicked, y_clicked)
            astroid_parser.add_click(x_clicked, y_clicked, left=True)
        elif event == cv2.EVENT_RBUTTONDOWN:
            point2 = (x_clicked, y_clicked)
            astroid_parser.add_click(x_clicked, y_clicked, left=False)
        
        preview_image_buffer = astroid_parser.request_preview_image()
        if preview_image_buffer is not None:
            preview_image = cv2.imdecode(np.frombuffer(preview_image_buffer.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow(window_image, preview_image)
        
        simple_coordinates_image_buffer = astroid_parser.request_simple_coordinates_image()
        if simple_coordinates_image_buffer is not None:
            simple_coordinates_image = cv2.imdecode(np.frombuffer(simple_coordinates_image_buffer.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow(window_simple_coordinates, simple_coordinates_image)
    cv2.setMouseCallback(window_image, mouse_callback)
    
    # keep alive
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    # cv2.destroyAllWindows()
    # plt.close()
    return astroid_parser.get_simple_coordinates()

def get_brush_blueprint(brush_size: int = 10) -> str:
    brush_blueprint_json = create_empty_blueprint_json()
    
    for x in range(brush_size):
        for y in range(brush_size):
            miner_blueprint = create_miner_json(x, y, (1, 0))
            brush_blueprint_json["BP"]["Entries"].append(miner_blueprint)
    
    brush_blueprint = json_to_blueprint(brush_blueprint_json)
    return brush_blueprint

def parse_using_blueprint(blueprint: str = "") -> Optional[list[tuple[int, int]]]:
    # checks
    if not blueprint or not blueprint.startswith(PREFIX):
        raise ValueError("Invalid or empty blueprint string")
    
    # try blueprint -> json
    try:
        blueprint_json = blueprint_to_json(blueprint)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode blueprint JSON: {e}")

    # get platform entries
    entires = blueprint_json["BP"]["Entries"]
    
    # get platform coodinate
    nodes: list[tuple[int, int]] = []
    for entry in entires:
        x = entry.get("X", 0)
        y = entry.get("Y", 0)
        nodes.append((x, y))
    
    # shifts coordinates
    min_x = min(x for x, _ in nodes)
    min_y = min(y for _, y in nodes)
    nodes = [(x - min_x, y - min_y) for x, y in nodes]
    
    # return
    return nodes

# if __name__ == "__main__":
#     # example usage
#     image_path = Path("images/example3.png")
#     simple_coordinates = astroid_parser(image_path, peak_threshold_rel=0.5)
#     print("Simple Coordinates:", simple_coordinates)

if __name__ == "__main__":
    # get the brush blueprint
    print(get_brush_blueprint())
    
    # the user brush out the asteroid shape and copy it here
    blueprint = input("Enter the blueprint string: ").strip()
    
    # convert the blueprint to simple coordinates
    simple_coordinates = parse_using_blueprint(blueprint)
    print("Simple Coordinates from Blueprint:", simple_coordinates)