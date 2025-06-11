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

def convert_miner_to_fluid(miner_blueprint : str, fluid_blueprint : Optional[str] = None) -> str:
    if fluid_blueprint is not None:    
        try:
            fluid_json = blueprint_to_json(fluid_blueprint)
            B = fluid_json["BP"]["Entries"][0]["B"]
        except json.JSONDecodeError:
            B = None
    else:
        B = None

    # print(B)

    # convert the miner blueprint to fluid miner blueprint
    
    # from miner_blueprint, create miner_blueprint_json
    miner_blueprint_json = blueprint_to_json(miner_blueprint)

    # replace miner externsion and belts
    for entry in miner_blueprint_json['BP']['Entries']:
        entry['T'] = entry['T'].replace("Belt", "Pipe")
        entry['T'] = entry['T'].replace("Shape", "Fluid")
            
    # insert platform json   
    for entry in miner_blueprint_json['BP']['Entries']:
        # skip if entry is not miner
        if entry['T'] != "Layout_FluidMiner":
            continue
        
        # clear the platform json if it is not provided
        if B is None:
            entry.pop("B", None)
            continue
        
        # get entry rotation
        R = entry.get("R", 0)
        
        # rotate platform json
        B_new = rotate_platform_json(B, R)
        
        # insert platform json
        entry['B'] = B_new
        
    # encode the blueprint
    blueprint = json_to_blueprint(miner_blueprint_json)
    
    # return
    return blueprint

# if __name__ == "__main__":    
#     # miner and belts layouts
#     (all_miner_platforms, all_extender_platforms, all_belts) = txt_to_var("variables.txt")
    
#     # miner blueprint (facing right)
#     miner_blueprint = "SHAPEZ2-3-H4sIAAPgQGgA/6yXUWujQBSF/8tlH33IaKKOj6FdCCQQ2hK6LGEZ6qQ7YMdyHemG4H9fbZrgbppEj0VQxPvNnZlzj5fZ0YoSIXzfo+mSkh19c9tXTQnNikzZlDyaPeW2+XCjnKLkJ5n6PVlmym1yfinIs2WW7W9U/FavOrkr9xetK49urWOjixrc0UM97Fxt89L9um8iF8ZqrjNM23mnpclSY5+/NPMjJaFHPyiZeHRXr9d7n8vtH8fqyeV8ozeqzNzMOs1WZSvFRllHlfdORjAZw6SESSFw1MfRAEfHQ9HmUbMBMmOM9QewAmcljsY4GuFoOHifwnZZTHXmPqi53lxRJ9wzC83Pmv2HXMwvV0L3+HHP+Ek7vrWG7zm/KU7PYeEZ7JOlLwxzzjr9j43ObF6nxDGw89GBPDDLnN29tqnmK3YI2iXSc7H+cYjLgpyAAQqOUXDyD9hXEhH0UuMD8s9sbbeUYoAw0XGIzvUQDi6HCNQmBjn5yYyv/xTkEG3kZWk6waMBuo6OQ/QrKQFyPsgFIDcGuQnIhSAXnXAd/QV01ahf04v7hcvTafV1INbs5MVe14WVQJ8cHUjEPxKzj8TcIzHzSMw7ErOOxJwjOxlnXZ9QjVW8XWkuTHMkbc7LVbWuqr8CDABeAPEsPg8AAA==$" 
    
#     print(compose_blueprint(all_miner_platforms, all_extender_platforms, all_belts, miner_blueprint = miner_blueprint))

if __name__ == "__main__":
    # miner blueprint
    miner_platforms_blueprint = "SHAPEZ2-3-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$"

    # convert to fluid blueprint
    fluid_platforms_blueprint = convert_miner_to_fluid(miner_platforms_blueprint, fluid_blueprint="SHAPEZ2-3-H4sIAIAbSmgA/6yXbUvDMBSF/8vFj/1g2sa1/ThfYDJh+DIUGRLWTIM1LWmKjNH/brtuWue0vXdSKITt2bnn3JuRrGAKEWOu68BwAtEKjuwykxDBKE+EjsGB0TzV9QdnwgqIHkFV62iSCLtIzVsOji6SpHlB/iIyGV0XzQOz0oFzbY2SeQWu4Lb62bFYpoV9ukgKFV8pLU2lMGzrDguVxEo//6vyfeXRd+ABIu7AdbVw1sVMirfsTC5EkdiRttJokUyFUUJbKJ2GYiTKJVHeARUGpAoDUoVYyj+Aqu0R4kBjLg3zDirSpxXp04r0aQ3wSd5OvlEqk2O56PDVIN4XclnouVWp/tsXGvNpGN9iW+AiNe/CxL99/2S/zF85NMhgN7oOoSbwEB94SAs8pAUe0gIPkTnU3rBBbBh0EnjOJ3L8k8OFwQlhcGIYnBgGJ4bBkVuxDXTvws3/nocV8WhYMxEuOgS2y91lQzF/7aFYkeM12X9ABjtkzaxPcpPU2BupY2k6RI/baB+bgz0cSjKkKYYEwcH2nIMmeeuE1CrV7dvMYH8vu6y24R+D1D0InyCxKYzWFEYfPEYcPEaYg802IVXLWi3xsP1kLZenJs3z7jpJeeKTpMwJwklIUAhQCkE/hVl1p1VamOVUmlzVl9j6hl2Ws7L8EECAAQDqSXdLcA8AAA==$")

    # print result
    print(fluid_platforms_blueprint)