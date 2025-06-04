
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

def encode_miner(x, y, direction):
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
        "T": "Layout_ShapeMiner",
    }

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
    blueprint_str = "SHAPEZ2-3-H4sIAGm7QGgA/yRNywrCMBD8l8FjLu1xj2IPBYWi4kWKLBoxEDel2YAl5N9NKQMDw7wybqCmaVuD/QDK2OkyWRD66FleMOifQVbjwMqgO1zVNHjWd5i/EUaS9xshfniydE4bMBaDTnR2NtZixrXOHnkJSR+XNXlyYufup1aiqx9lLOUvgAADAEnSHn2PAAAA$"

    # print(decode_blueprint(blueprint_str))

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
    
    
    plot_imported_result(all_miner_platforms, all_extender_platforms, all_belts)
    
    
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
            miner = encode_miner(x, y, direction)
            
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

    print(encode_blueprint(empty_json))
