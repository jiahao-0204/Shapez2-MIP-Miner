# system
from __future__ import annotations
from typing import List, Tuple, Dict, Optional
import copy
import json
import gzip
import base64


PREFIX = "SHAPEZ2-3-"

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

class Building():
    def __init__(self, T: str = "TrashDefaultInternalVariant", R: int = 0):
        self.T = T
        self.R = R 

    def rotate(self):
        self.R = (self.R + 1) % 4

    def rotate_R(self, R: int):
        for _ in range(R):
            self.rotate()

    def to_entry(self, X: int = 0, Y: int = 0, L: int = 0):
        entry = {}
        if X != 0:
            entry["X"] = X
        if Y != 0:
            entry["Y"] = Y
        if L != 0:
            entry["L"] = L
        if self.R != 0:
            entry["R"] = self.R
        entry["T"] = self.T
        return entry
    
    def to_blueprint(self):
        building_space = BuildingSpace()
        building_space.add_building(self)
        return building_space.to_blueprint()

types_of_platforms = [
    "Foundation_1x1",
    "Foundation_2x2",
    "Foundation_3x3",
]

types_of_buildings = [
    "TrashDefaultInternalVariant",
    "BeltDefaultForwardInternalVariant",
]

class Platform():
    def __init__(self, T: str = "Foundation_1x1", R: int = 0):
        self.T = T
        self.R = R
        self.platform_size = 20
        self.buildings : Dict[Tuple[int, int, int], Building] = {}

    def rotate(self):
        # rotate R of each building
        self.R = (self.R + 1) % 4

        # rotate each building
        new_buildings : Dict[Tuple[int, int, int], Building] = {}
        for (x, y, z), building in self.buildings.items():
            building.rotate_R(1)
            new_x = self.platform_size - y - 1
            new_y = x
            new_buildings[(new_x, new_y, z)] = building
        self.buildings = new_buildings

    def rotate_R(self, R: int):
        for _ in range(R):
            self.rotate()

    def add_building(self, building: Building, X: int = 0, Y: int = 0, L: int = 0, R: int = 0):        
        # deep copy the building
        building = copy.deepcopy(building)
        building.rotate_R(R)
        self.buildings[(X, Y, L)] = building
        
    def to_entry(self, X: int = 0, Y: int = 0, Z: int = 0):
        entry = {}
        if X != 0:
            entry["X"] = X
        if Y != 0:
            entry["Y"] = Y
        if Z != 0:
            entry["Z"] = Z
        if self.R != 0:
            entry["R"] = self.R
        entry["T"] = self.T
        
        building_entries = []
        for (x, y, z), building in self.buildings.items():
            building_entries.append(building.to_entry(x, y, z))
        if building_entries:
            entry["B"] = {
                "$type": "Building",
                "Entries": building_entries
                }
        return entry

    def to_blueprint(self):
        platform_space = PlatformSpace()
        platform_space.add_platform(self)
        return platform_space.to_blueprint()
        

class BuildingSpace():
    def __init__(self):
        self.buildings : Dict[Tuple[int, int, int], Building] = {}
    
    def add_building(self, building: Building, X: int = 0, Y: int = 0, L: int = 0, R: int = 0):
        # deep copy the building
        building = copy.deepcopy(building)
        building.rotate_R(R)
        self.buildings[(X, Y, L)] = building
    
    def to_blueprint(self):
        blueprint_json = {
            "V": 1122,
            "BP": {
                "$type": "Building",
                "Entries": [building.to_entry(x, y, z) for (x, y, z), building in self.buildings.items()],
            }
        }
        return json_to_blueprint(blueprint_json)
        

class PlatformSpace():
    def __init__(self):
        self.platforms : Dict[Tuple[int, int, int], Platform] = {}
    
    def add_platform(self, platform: Platform, X: int = 0, Y: int = 0, Z: int = 0, R: int = 0):
        # deep copy
        platform = copy.deepcopy(platform)
        platform.rotate_R(R)
        self.platforms[(X, Y, Z)] = platform
    
    def to_blueprint(self):
        blueprint_json = {
            "V": 1122,
            "BP": {
                "$type": "Island",
                "Entries": [platform.to_entry(x, y, z) for (x, y, z), platform in self.platforms.items()],
            }
        }
        return json_to_blueprint(blueprint_json)

if __name__ == "__main__":
    # print(json.dumps(blueprint_to_json("SHAPEZ2-3-H4sIAKuMTGgA/5SRTQvCMAyG/8uLx3rYvPXoFwgKIjIm4iG4TAulk6xDxth/t1MUUYRJoSSEJw/kbZBAR1EcK4zX0A0Gvr4wNMaVsZlxJygsjoXrRlPyBL2HCb1+zksoV1n7+FCe6cJ6Uj0eDq3CzHkxXAawQQo9DKZdUCpsoEO97Vxs/ZRzqqxfcu4XzrM4sgmJIedXRqQQztCq14bAjr7YeSFXkuwDf8eCeBj9oPuYo9eK/uq/gfR+nf+wQ4jPOJI6YSlNF1eXadveBBBgAEYgmkPfAQAA$"), indent=4))
    # BeltDefaultForwardInternalVariant
    # TrashDefaultInternalVariant
    building = Building(T="BeltDefaultForwardInternalVariant", R = 0)
    platform = Platform(T="Foundation_1x1")
    platform.add_building(building, X=3, Y=3, L=0, R=1)
    space = PlatformSpace()
    space.add_platform(platform, 0, 0, 0, 1)
    space.add_platform(platform, 1, 0, 0, 2)
    space.add_platform(platform, 2, 0, 0, 3)
    space.add_platform(platform, 3, 0, 0, 4)
    print(space.to_blueprint())