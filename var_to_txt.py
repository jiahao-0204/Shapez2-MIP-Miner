# system
from typing import List, Tuple

# thrid party
from gurobipy import Var

class FakeVar:
    """
    A fake variable class to mimic Gurobi's Var class.
    This is used to create a variable with a name and value.
    """
    def __init__(self, VarName: str = "", X: float = 0.0):
        self.VarName = VarName
        self.X = X
        pass

    def setAttr(self, attr, value):
        setattr(self, attr, value)

    def __repr__(self):
        return f"FakeVar(VarName={self.VarName}, X={self.X})"


def var_to_txt(filename : str, all_extender_platforms : List[FakeVar], all_miner_platforms : List[FakeVar], all_belts : List[FakeVar]) -> None:
    # save the variables to a file
    with open(filename, "w") as f:
        f.write("All Extender Platforms:\n")
        for extender in all_extender_platforms:
            f.write(f"{extender.VarName}: {extender.X}\n")
        
        f.write("\nAll Miner Platforms:\n")
        for miner in all_miner_platforms:
            f.write(f"{miner.VarName}: {miner.X}\n")
        
        f.write("\nAll Belts:\n")
        for belt in all_belts:
            f.write(f"{belt.VarName}: {belt.X}\n")



def txt_to_var(filename : str) -> Tuple[List[FakeVar], List[FakeVar], List[FakeVar]]:
    all_miner_platforms = []
    all_extender_platforms = []
    all_belts = []
    with open("variables.txt", "r") as f:
        lines = f.readlines()
        section = None
        for line in lines:            
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if line.startswith("All Extender Platforms:"):
                section = "extenders"
                continue
            elif line.startswith("All Miner Platforms:"):
                section = "miners"
                continue
            elif line.startswith("All Belts:"):
                section = "belts"
                continue
            
            if section == "extenders":
                parts = line.split(": ")
                var = FakeVar()
                var.setAttr("VarName", parts[0])
                var.setAttr("X", int(abs(float(parts[1]))))
                all_extender_platforms.append(var)
            elif section == "miners":
                parts = line.split(": ")
                var = FakeVar()
                var.setAttr("VarName", parts[0])
                var.setAttr("X", int(abs(float(parts[1]))))
                all_miner_platforms.append(var)
            elif section == "belts":
                parts = line.split(": ")
                var = FakeVar()
                var.setAttr("VarName", parts[0])
                var.setAttr("X", int(abs(float(parts[1]))))
                all_belts.append(var)
    
    return (all_miner_platforms, all_extender_platforms, all_belts)