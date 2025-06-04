# system
from typing import List, Tuple, Dict
import copy

# third party
import base64, gzip, json
import matplotlib.pyplot as plt

# project
from var_to_txt import txt_to_var

PREFIX = "SHAPEZ2-3-"


def decode_blueprint(blueprint_str):
    """
    Decodes a Shapez.io blueprint string into a human-readable format.
    
    Args:
        blueprint_str (str): The encoded blueprint string.
        
    Returns:
        str: The decoded blueprint in JSON format or as plain text if not JSON.
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
        return json.dumps(decoded_json, indent=2)
    except json.JSONDecodeError:
        return decoded_text

def encode_blueprint(decoded_text):
    """
    Encodes a decoded blueprint back into the Shapez.io format.
    
    Args:
        decoded_text (str): The decoded blueprint in JSON or plain text format.
        
    Returns:
        str: The encoded blueprint string.
    """
    
    # if input is dict, convert to string
    if isinstance(decoded_text, dict):
        decoded_text = json.dumps(decoded_text)
    
    # try to parse as JSON to ensure it's in the correct format
    # if it fails, keep it as plain text
    if isinstance(decoded_text, str):
        try:
            decoded_json = json.loads(decoded_text)
            decoded_text = json.dumps(decoded_json)
        except json.JSONDecodeError:
            pass  # Keep as plain text if it fails

    # GZip compress
    compressed_bytes = gzip.compress(decoded_text.encode("utf-8"))

    # Base‑64 encode
    compressed_b64 = base64.b64encode(compressed_bytes).decode("utf-8")

    # Add the prefix back
    return f"{PREFIX}{compressed_b64}{"$"}"

def encode_miner(x, y, direction, B = None):
    if direction == (1, 0):
        R = 0
    elif direction == (0, -1):
        R = 1
    elif direction == (-1, 0):
        R = 2
    elif direction == (0, 1):
        R = 3
    
    entry = {
        "x": x,
        "y": -y,
        "R": R,
        "T": "Layout_ShapeMiner",
    }
    
    # add platform code / B if it exists
    if B is not None:
        entry["B"] = B
        entry["B"] = rotate_platform(B, R)
    
    return entry

def rotate_coordinates(x, y):
    N = 20  # assuming a 20x20 grid
    return N - 1 - y, x

def rotate_platform(platform_B_code, R):
    # deep copy the miner_B to avoid modifying the original
    platform_B_code_copy = copy.deepcopy(platform_B_code)    
    
    # goes through each entry, add R to the R value if it exists, R assumed to be 0 if it does not exist
    for entry in platform_B_code_copy["Entries"]:
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
    return platform_B_code_copy

def encode_extender(x, y, direction):
    if direction == (1, 0):
        R = 0
    elif direction == (0, -1):
        R = 1
    elif direction == (-1, 0):
        R = 2
    elif direction == (0, 1):
        R = 3
    
    return {
        "x": x,
        "y": -y,
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

def plot_imported_result(all_miner_platforms, all_extender_platforms, all_belts):
    # initialize plt
    # colors
    edge_color = 'black'
    belt_color = 'blue'
    miner_color = 'green'
    miner_belt_color = belt_color
    extender_color = 'orange'
    extender_belt_color = 'black'
    
    width = 30
    height = 30
    plt.figure(figsize=(6, 6))
    plt.xlim(-1, width+1)
    plt.ylim(-1, height+1)
    # plt.grid(True)
    plt.xticks(range(width+1))
    plt.yticks(range(height+1))
    plt.gca().set_aspect('equal', adjustable='box')
    # include first optimization objective in the title
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    # plt.axhline(0, color='black', lw=0.5)
    # plt.axvline(0, color='black', lw=0.5)
        
    # draw belts
    for belt in all_belts:
        if belt.X > 0.5:  # if the belt is placed
            start_node = tuple(map(int, belt.VarName.split('_')[1:3]))
            end_node = tuple(map(int, belt.VarName.split('_')[3:5]))
            plt.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], color=belt_color, linewidth=2, zorder = 1)
    
    # draw miners
    for miner in all_miner_platforms:
        if miner.X > 0.5:  # if the miner is placed
            start_node = tuple(map(int, miner.VarName.split('_')[1:3]))
            end_node = tuple(map(int, miner.VarName.split('_')[3:5]))
            
            # compute direction
            direction = (end_node[0] - start_node[0], end_node[1] - start_node[1])

            if direction == (1, 0):  # right
                marker = '>'
            elif direction == (0, 1):  # up
                marker = '^'
            elif direction == (-1, 0):  # left
                marker = '<'
            elif direction == (0, -1):  # down
                marker = 'v'
            else:
                marker = '.'
            
            # draw miner
            plt.scatter(start_node[0], start_node[1], color=miner_color, marker=marker, s=80, edgecolors=edge_color, zorder=2)
            
            # draw line to belt
            plt.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], color=belt_color, linewidth=2, zorder = 1)
            
    # draw extenders
    for extender in all_extender_platforms:
        if extender.X > 0.5:  # if the extender is placed
            start_node = tuple(map(int, extender.VarName.split('_')[1:3]))
            end_node = tuple(map(int, extender.VarName.split('_')[3:5]))
            
            # draw extender
            plt.scatter(start_node[0], start_node[1], color=extender_color, marker='o', s=80, edgecolors=edge_color, zorder=2)
            
            # draw line to miner or extender
            plt.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], color=extender_belt_color, linewidth=1, zorder = 1)
    
    plt.show()

if __name__ == "__main__":
    # Blueprint string provided by the user
    blueprint_str = "SHAPEZ2-3-H4sIAFzXQGgA/6yQQWvDMAyF/8ujR1/SQQ8+hrSQWwkltIwwRONuBlcutsxWgv/7HHLJtVAEEkI8fXqa0ENX1XarUB+hJ2zk+TDQaKMjHqHQXj3Pg4aEoD9hS6+PjuTmwz1CcXJuSYg/9DC6S0tgyAp7lmBNLMIJXSEpnMryg088kljPX9VfVSD1Gl0n60bL32+Fnwt8p3CB/lCrS2rjpDE3Sk4OPvxSGFsWE5hcT8ESC7Jai+fyknoo5ixTePYmRDu7mb+d85DzvwADAOgwhKF8AQAA$"

    # print(decode_blueprint(blueprint_str))

    # paste the blueprint for the miner, the output must face right / east
    miner_blueprint = "SHAPEZ2-3-H4sIAAPgQGgA/6yXUWujQBSF/8tlH33IaKKOj6FdCCQQ2hK6LGEZ6qQ7YMdyHemG4H9fbZrgbppEj0VQxPvNnZlzj5fZ0YoSIXzfo+mSkh19c9tXTQnNikzZlDyaPeW2+XCjnKLkJ5n6PVlmym1yfinIs2WW7W9U/FavOrkr9xetK49urWOjixrc0UM97Fxt89L9um8iF8ZqrjNM23mnpclSY5+/NPMjJaFHPyiZeHRXr9d7n8vtH8fqyeV8ozeqzNzMOs1WZSvFRllHlfdORjAZw6SESSFw1MfRAEfHQ9HmUbMBMmOM9QewAmcljsY4GuFoOHifwnZZTHXmPqi53lxRJ9wzC83Pmv2HXMwvV0L3+HHP+Ek7vrWG7zm/KU7PYeEZ7JOlLwxzzjr9j43ObF6nxDGw89GBPDDLnN29tqnmK3YI2iXSc7H+cYjLgpyAAQqOUXDyD9hXEhH0UuMD8s9sbbeUYoAw0XGIzvUQDi6HCNQmBjn5yYyv/xTkEG3kZWk6waMBuo6OQ/QrKQFyPsgFIDcGuQnIhSAXnXAd/QV01ahf04v7hcvTafV1INbs5MVe14WVQJ8cHUjEPxKzj8TcIzHzSMw7ErOOxJwjOxlnXZ9QjVW8XWkuTHMkbc7LVbWuqr8CDABeAPEsPg8AAA==$" 
    
    # extract platform B code from the miner blueprint
    decoded_miner = decode_blueprint(miner_blueprint)
    B = json.loads(decoded_miner)["BP"]["Entries"][0]["B"]
    
    # print(json.dumps(B, indent=2))
    # print(json.dumps(rotate_miner(B, 1), indent=2))
    
    # empty_json = {
    #     "v": 1122,
    #     "BP": {
    #         "$type": "Island",
    #         "Icon": {
    #             "Data": [
    #                 "icon:Platforms",
    #                 None,
    #                 None,
    #                 "shape:RuRuRuRu"
    #             ]
    #         },
    #         "Entries": []
    #     }
    # }
    
    # # rotated_miner = encode_miner(0, 0, (1, 0), B)
    # rotated_miner = encode_miner(0, 0, (-1, 0), B)
    # # rotated_miner = encode_miner(0, 0, (1, 0), B)
    # # rotated_miner = encode_miner(0, 0, (1, 0), B)
    # empty_json['BP']['Entries'].append(rotated_miner)
    
    # print(json.dumps(empty_json, indent=2))
    # print(encode_blueprint(empty_json))
    
    
    # # print(json.dumps(B, indent=2))
    # print(decode_blueprint(miner_blueprint))
            

    # ------------------
    
    (all_miner_platforms, all_extender_platforms, all_belts) = txt_to_var("variables.txt")
    
    
    # print("All Extender Platforms:")
    # for extender in all_extender_platforms:
    #     print(f"{extender['VarName']}: {extender['X']}")
    
    # print("\nAll Miner Platforms:")
    # for miner in all_miner_platforms:
    #     print(f"{miner['VarName']}: {miner['X']}")
    
    # print("\nAll Belts:")
    # for belt in all_belts:
    #     print(f"{belt['VarName']}: {belt['X']}")
    
    
    # plot_imported_result(all_miner_platforms, all_extender_platforms, all_belts)
    
    
    empty_json = {
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
            miner = encode_miner(x, y, direction, B)
            
            # add miner to the blueprint
            empty_json['BP']['Entries'].append(miner)
    
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
            extender = encode_extender(x, y, direction)
            
            # add extender to the blueprint
            empty_json['BP']['Entries'].append(extender)
    
    # empty_json['BP']['Entries'].append(miner)
    
    
    # create a map of node to io
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
                encoded_belt = {
                    "x": belt.x,
                    "y": -belt.y,
                    "R": r,
                    "T": belt_type,
                }
                empty_json['BP']['Entries'].append(encoded_belt)
    
    # print(json.dumps(empty_json, indent=2))
    print(encode_blueprint(empty_json))
