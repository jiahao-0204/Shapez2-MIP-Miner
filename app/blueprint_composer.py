# system
from typing import List, Tuple, Dict, Optional
import copy

# third party
import base64, gzip, json
import matplotlib.pyplot as plt

# project
from app.var_to_txt import txt_to_var, FakeVar

PREFIX = "SHAPEZ2-3-"


def blueprint_to_json(blueprint_str) -> dict:
    """
    Decodes a Shapez.io blueprint string into a human-readable format.
    
    Args:
        blueprint_str (str): The encoded blueprint string.
        
    Returns:
        dict: The decoded blueprint in JSON format or as plain text if not JSON.
    """
    # remove prefix
    compressed_b64 = blueprint_str[len(PREFIX):]

    # Base‑64 decode
    compressed_bytes = base64.b64decode(compressed_b64)

    # GZip‑decompress
    decompressed_bytes = gzip.decompress(compressed_bytes)
    decoded_text = decompressed_bytes.decode("utf-8")
    
    # try to parse as JSON for nicer formatting
    try:
        decoded_json = json.loads(decoded_text)
        return decoded_json
    except json.JSONDecodeError:
        raise

def json_to_blueprint(json_str):
    """
    Encodes a decoded blueprint back into the Shapez.io format.
    
    Args:
        decoded_text (str): The decoded blueprint in JSON or plain text format.
        
    Returns:
        str: The encoded blueprint string.
    """
    
    # if input is dict, convert to string
    if isinstance(json_str, dict):
        json_str = json.dumps(json_str)
    
    # try to parse as JSON to ensure it's in the correct format
    # if it fails, keep it as plain text
    if isinstance(json_str, str):
        try:
            decoded_json = json.loads(json_str)
            json_str = json.dumps(decoded_json)
        except json.JSONDecodeError:
            pass  # Keep as plain text if it fails

    # GZip compress
    compressed_bytes = gzip.compress(json_str.encode("utf-8"))

    # Base‑64 encode
    compressed_b64 = base64.b64encode(compressed_bytes).decode("utf-8")

    # Add the prefix back
    return f"{PREFIX}{compressed_b64}{'$'}"

def create_elevator_json(x, y, direction):
    """
    Creates a JSON representation of an elevator in Shapez.io.
    
    Args:
        x (int): The x-coordinate of the elevator.
        y (int): The y-coordinate of the elevator.
        direction (tuple): The direction of the elevator as a tuple (dx, dy).
        
    Returns:
        dict: A dictionary representing the elevator in Shapez.io format.
    """
    if direction == (1, 0):
        R = 0
    elif direction == (0, -1):
        R = 1
    elif direction == (-1, 0):
        R = 2
    elif direction == (0, 1):
        R = 3
    
    return {
        "X": x,
        "Y": -y,
        "R": R,
        "T": "SpaceBelt_Lift1UpForward",
    }

def create_miner_json(x, y, direction, platform_json = None) -> dict:
    if direction == (1, 0):
        R = 0
    elif direction == (0, -1):
        R = 1
    elif direction == (-1, 0):
        R = 2
    elif direction == (0, 1):
        R = 3
    
    entry = {
        "X": x,
        "Y": -y,
        "R": R,
        "T": "Layout_ShapeMiner",
    }
    
    # add platform code / B if it exists
    if platform_json is not None:
        entry["B"] = platform_json
        entry["B"] = rotate_platform_json(platform_json, R)
    
    return entry

def rotate_coordinates(x, y):
    N = 20  # assuming a 20x20 grid
    return N - 1 - y, x

def rotate_platform_json(platform_json, R):
    # deep copy the miner_B to avoid modifying the original
    platform_json_copy = copy.deepcopy(platform_json)    
    
    # goes through each entry, add R to the R value if it exists, R assumed to be 0 if it does not exist
    for entry in platform_json_copy["Entries"]:
        # change R for individual element
        if "R" in entry:
            entry["R"] = (entry["R"] + R) % 4
        else:
            entry["R"] = R
        
        # change X and Y coordinates for individual element
        x = entry["X"]
        y = entry["Y"]
        for i in range(R):
            x, y = rotate_coordinates(x, y)
        entry["X"] = x
        entry["Y"] = y

    # return the modified platform_B_code
    return platform_json_copy

def create_extender_json(x, y, direction):
    if direction == (1, 0):
        R = 0
    elif direction == (0, -1):
        R = 1
    elif direction == (-1, 0):
        R = 2
    elif direction == (0, 1):
        R = 3
    
    return {
        "X": x,
        "Y": -y,
        "R": R,
        "T": "Layout_ShapeMinerExtension",
    }

def invert_tuple(t):
    return (-t[0], -t[1])
class SpaceBelt:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.input_location : List[tuple[int, int]] = []
        self.output_location : List[tuple[int, int]] = []
    
    def direction_to_r(self, direction):
        if direction == (1, 0):
            return 0
        elif direction == (0, -1):
            return 1
        elif direction == (-1, 0):
            return 2
        elif direction == (0, 1):
            return 3
        else:
            raise ValueError("Invalid direction")
    
    def get_type(self):
        in_count = len(self.input_location)
        out_count = len(self.output_location)
        
        if in_count == 0 and out_count == 0:
            return None, None
        elif in_count == 3 and out_count == 1:
            return "SpaceBelt_TripleMerger", self.direction_to_r(self.output_location[0])
        elif in_count == 1 and out_count == 3:
            return "SpaceBelt_TripleSplitter", self.direction_to_r(invert_tuple(self.input_location[0]))
        elif in_count == 2 and out_count == 1:
            # could be
            # - SpaceBelt_YMerger
            # - SpaceBelt_LeftFwdMerger
            # - SpaceBelt_RightFwdMerger
            
            # sum vector
            sum_vector = (0, 0)
            for loc in self.input_location:
                sum_vector = (sum_vector[0] + loc[0], sum_vector[1] + loc[1])
            for loc in self.output_location:
                sum_vector = (sum_vector[0] + loc[0], sum_vector[1] + loc[1])

            # output vector
            output_vector = self.output_location[0]
            
            # check if y merger
            if sum_vector == output_vector:
                return "SpaceBelt_YMerger", self.direction_to_r(self.output_location[0])
            
            # check if left or right
            cross_product = sum_vector[0] * output_vector[1] - sum_vector[1] * output_vector[0]
            if cross_product > 0:
                return "SpaceBelt_LeftFwdMerger", self.direction_to_r(self.output_location[0])
            elif cross_product < 0:
                return "SpaceBelt_RightFwdMerger", self.direction_to_r(self.output_location[0])
        elif in_count == 1 and out_count == 2:
            # could be
            # - SpaceBelt_LeftFwdSplitter
            # - SpaceBelt_RightFwdSplitter
            # - SpaceBelt_YSplitter
                        
            # sum vector
            sum_vector = (0, 0)
            for loc in self.input_location:
                sum_vector = (sum_vector[0] + loc[0], sum_vector[1] + loc[1])
            for loc in self.output_location:
                sum_vector = (sum_vector[0] + loc[0], sum_vector[1] + loc[1])
                
            # input vector
            input_vector = self.input_location[0]
            
            # check if y splitter
            if sum_vector == input_vector:
                return "SpaceBelt_YSplitter", self.direction_to_r(invert_tuple(self.input_location[0]))
            
            # check if left or right
            cross_product = sum_vector[0] * input_vector[1] - sum_vector[1] * input_vector[0]
            if cross_product > 0:
                return "SpaceBelt_LeftFwdSplitter", self.direction_to_r(self.output_location[0])
            elif cross_product < 0:
                return "SpaceBelt_RightFwdSplitter", self.direction_to_r(self.output_location[0])
        elif in_count == 1 and out_count == 1:
            # could be
            # - SpaceBelt_Forward
            # - SpaceBelt_LeftTurn
            # - SpaceBelt_RightTurn
                        
            # sum vector
            sum_vector = (0, 0)
            for loc in self.input_location:
                sum_vector = (sum_vector[0] + loc[0], sum_vector[1] + loc[1])
            for loc in self.output_location:
                sum_vector = (sum_vector[0] + loc[0], sum_vector[1] + loc[1])
            
            # check if it is a forward belt
            if sum_vector == (0, 0):
                return "SpaceBelt_Forward", self.direction_to_r(self.output_location[0])
            
            # check if it is a left or right turn
            input_vector = self.input_location[0]
            output_vector = self.output_location[0]
            cross_product = sum_vector[0] * output_vector[1] - sum_vector[1] * output_vector[0]
            if cross_product < 0:
                return "SpaceBelt_LeftTurn", self.direction_to_r(invert_tuple(self.input_location[0]))
            elif cross_product > 0:
                return "SpaceBelt_RightTurn", self.direction_to_r(invert_tuple(self.input_location[0]))
        else:
            # throw error
            return None

def create_empty_blueprint_json() -> dict:
    """
    Creates an empty blueprint JSON structure.
    
    Returns:
        dict: An empty blueprint JSON structure.
    """
    return {
        "v": 1122,
        "BP": {
            "$type": "Island",
            "Icon": {
                "Data": [
                    "icon:Platforms",
                    None,
                    None,
                    "shape:RuRuRuRu"
                ]
            },
            "Entries": []
        }
    }

def compose_blueprint(all_miner_platforms: List[FakeVar], all_extender_platforms: List[FakeVar], all_belts: List[FakeVar], all_elevators: List[FakeVar] = [], miner_blueprint: Optional[str] = None) -> str:
    # extract platform B code from the miner blueprint if provided
    if miner_blueprint is not None:    
        try:
            miner_json = blueprint_to_json(miner_blueprint)
            B = miner_json["BP"]["Entries"][0]["B"]
        except json.JSONDecodeError:
            B = None
    else:
        B = None
    
    # initialize empty blueprint
    all_json = create_empty_blueprint_json()

    # add miner
    miner_and_belt_flow_to_from : Dict[Tuple[int, int], Tuple[int, int]] = {}
    for miner in all_miner_platforms:
        if miner.X > 0.5:
            # extract coordinates and direction from VarName
            parts = miner.VarName.split('_')
            x = int(parts[1])
            y = int(parts[2])
            x2 = int(parts[3])
            y2 = int(parts[4])
            direction = (x2 - x, y2 - y)
            
            # encode miner
            miner_json = create_miner_json(x, y, direction, B)
            
            # add miner to the blueprint
            all_json['BP']['Entries'].append(miner_json)
            
            # store the flow direction for the miner
            if (x2, y2) not in miner_and_belt_flow_to_from:
                # store the flow direction for the miner
                miner_and_belt_flow_to_from[(x2, y2)] = (x, y)
    
    # add extenders
    for extender in all_extender_platforms:
        if extender.X > 0.5:
            # extract coordinates and direction from VarName
            parts = extender.VarName.split('_')
            x = int(parts[1])
            y = int(parts[2])
            x2 = int(parts[3])
            y2 = int(parts[4])
            direction = (x2 - x, y2 - y)
            
            # encode extender
            extender_json = create_extender_json(x, y, direction)
            
            # add extender to the blueprint
            all_json['BP']['Entries'].append(extender_json)
        
    # add belts
    map_of_space_belts : Dict[Tuple[int, int], SpaceBelt] = {}
    for belt in all_belts:
        if belt.X > 0.5:
            # extract coordinates from VarName
            parts = belt.VarName.split('_')
            x = int(parts[1])
            y = int(parts[2])
            x2 = int(parts[3])
            y2 = int(parts[4])
            
            # create a space belt
            if (x, y) not in map_of_space_belts:
                map_of_space_belts[(x, y)] = SpaceBelt(x, y)
            if (x2, y2) not in map_of_space_belts:
                map_of_space_belts[(x2, y2)] = SpaceBelt(x2, y2)
            
            direction = (x2 - x, y2 - y)
            inv_direction = invert_tuple(direction)
            
            # add input and output locations
            map_of_space_belts[(x, y)].output_location.append(direction)
            map_of_space_belts[(x2, y2)].input_location.append(inv_direction)
            
            # add to flow direction map
            if (x2, y2) not in miner_and_belt_flow_to_from:
                miner_and_belt_flow_to_from[(x2, y2)] = (x, y)
                
    for miner in all_miner_platforms:
        if miner.X > 0.5:
            # extract coordinates and direction from VarName
            parts = miner.VarName.split('_')
            x = int(parts[1])
            y = int(parts[2])
            x2 = int(parts[3])
            y2 = int(parts[4])
            direction = (x2 - x, y2 - y)
            inv_direction = invert_tuple(direction)
            
            if (x2, y2) in map_of_space_belts:
                map_of_space_belts[(x2, y2)].input_location.append(inv_direction)
    for belt in map_of_space_belts.values():
        result = belt.get_type()
        if result is not None:
            belt_type, r = result
            if belt_type is not None:
                # encode belt
                belt_json = {
                    "x": belt.x,
                    "y": -belt.y,
                    "R": r,
                    "T": belt_type,
                }
                all_json['BP']['Entries'].append(belt_json)
    
    # add elevators
    for elevator in all_elevators:
        if elevator.X > 0.5:
            # extract coordinates and direction from VarName
            # elevator_var_name = f"elevator_{node[0]}_{node[1]}"
            parts = elevator.VarName.split('_')
            x = int(parts[1])
            y = int(parts[2])
            
            # elevator direction are obtained from miner out flow direction
            from_node = miner_and_belt_flow_to_from.get((x, y), None)
            
            if from_node is None:
                continue
            
            direction = (x - from_node[0], y - from_node[1])
            
            # encode elevator
            elevator_json = create_elevator_json(x, y, direction)
            
            # add elevator to the blueprint
            all_json['BP']['Entries'].append(elevator_json)
    
    # encode the blueprint
    blueprint = json_to_blueprint(all_json)
    
    # return
    return blueprint

if __name__ == "__main__":    
    # miner and belts layouts
    (all_miner_platforms, all_extender_platforms, all_belts) = txt_to_var("variables.txt")
    
    # miner blueprint (facing right)
    miner_blueprint = "SHAPEZ2-3-H4sIAAPgQGgA/6yXUWujQBSF/8tlH33IaKKOj6FdCCQQ2hK6LGEZ6qQ7YMdyHemG4H9fbZrgbppEj0VQxPvNnZlzj5fZ0YoSIXzfo+mSkh19c9tXTQnNikzZlDyaPeW2+XCjnKLkJ5n6PVlmym1yfinIs2WW7W9U/FavOrkr9xetK49urWOjixrc0UM97Fxt89L9um8iF8ZqrjNM23mnpclSY5+/NPMjJaFHPyiZeHRXr9d7n8vtH8fqyeV8ozeqzNzMOs1WZSvFRllHlfdORjAZw6SESSFw1MfRAEfHQ9HmUbMBMmOM9QewAmcljsY4GuFoOHifwnZZTHXmPqi53lxRJ9wzC83Pmv2HXMwvV0L3+HHP+Ek7vrWG7zm/KU7PYeEZ7JOlLwxzzjr9j43ObF6nxDGw89GBPDDLnN29tqnmK3YI2iXSc7H+cYjLgpyAAQqOUXDyD9hXEhH0UuMD8s9sbbeUYoAw0XGIzvUQDi6HCNQmBjn5yYyv/xTkEG3kZWk6waMBuo6OQ/QrKQFyPsgFIDcGuQnIhSAXnXAd/QV01ahf04v7hcvTafV1INbs5MVe14WVQJ8cHUjEPxKzj8TcIzHzSMw7ErOOxJwjOxlnXZ9QjVW8XWkuTHMkbc7LVbWuqr8CDABeAPEsPg8AAA==$" 
    
    print(compose_blueprint(all_miner_platforms, all_extender_platforms, all_belts, miner_blueprint = miner_blueprint))

# if __name__ == "__main__":
#     blueprint = "SHAPEZ2-3-H4sIAPCSR2gA/ySMywrCMBRE/2VwmU26vMuiQsFF8bWRIpc2xUBMQ3KLSMi/GykDA8NhTsYdpHXTKLQ9KGMn32BA6JJjP0GhGxf/B3sWBj1g66bescxLfCcovzq3FdKLg6HzugVDUTh4idakesy4Vu0l8Gha4+R5srPoWzgu8cNxQhlK+QkgwADAG5kVjQAAAA==$"
    
#     blueprint_json = blueprint_to_json(blueprint)
#     print(json.dumps(blueprint_json, indent=4))