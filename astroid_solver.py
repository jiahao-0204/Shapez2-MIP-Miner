# system
from typing import List, Tuple, Dict, Optional
from collections import defaultdict
from pathlib import Path
from io import BytesIO

# third party
from gurobipy import Model, GRB, quicksum, Var, LinExpr
from matplotlib import pyplot as plt
import cv2
import numpy as np

# project
from astroid_parser import astroid_parser
from var_to_txt import var_to_txt, FakeVar
from blueprint_composer import compose_blueprint

DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

class AstroidSolver:
    def __init__(self):
        # general settings
        self.BELT_MAX_FLOW = 12 * 4
        
        # margin for the board
        self.MARGIN_X = 5
        self.MARGIN_Y = 5
        
        # default blueprint
        self.default_blueprint = "SHAPEZ2-2-H4sIAN0dd2cA/6xaXW+bMBT9L9Ye0YTNl0Haw7J2UrVEqtqs2jRVE0qcDo1C5JBtUZX/PhIMNRCofU37ELXhnHt8fX2uDbygBxRhbHsWmt2i6AW9Kw5bhiJ0s0vjbI0sdLPKs9MXV3ERo+gHSsq/o+rb2zResWeWFeVl53+n8SHfF+/n54+f97/iLVskGePIyvZpKi66ft4WB/R4tNB1VvCE7UrWF7QsY17AoZksarZP0nWSPQ3JKgUVm5w/70TAKuruxBfd7avfXuRvKPIt9B1FZQ7uUORYZy3X/woer4qcX7FNvE+Lm6xgPIvTh5gncTnio3VGBmAklZBYCxmCkZVaV1Y7Y2khQHO26QIXCec5Z+uawO8TzJNNgb9uFcBN9HmjW4r+Oed/Y74ezRYMizF4kgRUccA9sbXM25wX9yxbM95FWOhTec2Xj+efD01Y5xLDHVux5M8QRwl/xRNwiYjQIKgLz7MrD3jB+BPjZJnj+Rslhb1uotRrWWBbI9WsR38Aq7wYKgKiGdwfxY4UpqgLA9liQcB0Y9sAHPalD9dJp5p90BxXEQOD+jiFV7XadmEIJKwyBsEqE2ybxA8vDFt9NQs0GUia0tBdcFsEQakMdQBtHAQVgj31ddzJUgv5dkN7jQdu3UCw8BvQ3NRYxcF2q/FVt2Eb71Jo93FQjdTBXXg7hmXdbQ1awaO9XpYUOpl3YXTqVUXA9lwXFcwf60lxYLK9AYPULkxPam0OuDq9CQbT2gxUxbI8HwDHywuy+XEN+rlQS1smMotXv8cwbo2pjA8oOJTwGLBGQpjx+ibgRjlcM1AtRCeVdd5v06Qor8bL3BlfxVSe0lNJkNEmKlBVRgkgNW4bD6lfINg3ARNp2RG4ZwXDNBqW5Yx6gPIdkEDzGEJk4zZOwmUe7SwMbrTf3j8S2AZfoLHBBp+C7Nsf9SOlg4Wt3KICeZRYp2METajG8R34zYVasoKjBVJ+nJah6SiGm1otVXsrZMOsTB/ndqYGqhbeiqFotzNFBsqJkXICOzja5gcwG+qUdCDzBkL6REA5ZCo54D4SNizgu2sYq+/8bbn3aPlqDcWmxioRqe4VbTlJWt7aVg0xV9xSC6oU/yKFxl4Dd1I/gRKTJdTWQ6bSA9+LBfLBUkXI4qkjJOiefYAMOk47RIGNKahuoQznYxIeffMfyc0kRFS3dEczRKbKEJkqQwZEocEZITQ4IwirvnCrRqtBUcnpTfpTaw2pN6mg3x7P8q/yv5nyAIBNiho7MTVsCXSiDkUnaVB0ov5EDduT3X7xAvxM0O0vDYU9X/Oqy8gdUMXHxoYMgQFDvZHzjLPYonA004jd0e2v6pNdUwpiToHNKWxjitCYoeUUo9P4aKFZksX88MD4Ljm9+XZ6Z+94fDwe/wsgwABYhMLTwicAAA==$"
        
    def add_astroid_locations(self, astroid_location: np.ndarray) -> None:
        # define board size
        width = max(x for x, y in astroid_location) + 2 * self.MARGIN_X
        height = max(y for x, y in astroid_location) + 2 * self.MARGIN_Y
        
        # list of all nodes
        nodes = [(x, y) for x in range(width) for y in range(height)]
        
        # list of source nodes
        nodes_to_extract = [(x + self.MARGIN_X, y + self.MARGIN_Y) for x, y in astroid_location]
                        
        # list of sink nodes
        x_min_sink = 0
        x_max_sink = width
        y_sink = height - 1
        nodes_sink = [(x, y_sink) for x in range(x_min_sink, x_max_sink)]
        
        # ----------------------------------------------------------
        # initialize the model
        # ----------------------------------------------------------
        model = Model("astroid_miner")
        
        # ----------------------------------------------------------
        # create some variables to use later
        # ----------------------------------------------------------
        
        all_extender_platforms = []
        all_miner_platforms = []
        all_belts = []
        all_flows = []
        
        node_extenders : Dict[Tuple[int, int], List[Var]] = defaultdict(list)
        node_miners : Dict[Tuple[int, int], List[Var]] = defaultdict(list)
        node_belts : Dict[Tuple[int, int], List[Var]] = defaultdict(list)
        node_flow_out : Dict[Tuple[int, int], List[Var]] = defaultdict(list)
        node_flow_in : Dict[Tuple[int, int], List[Var]] = defaultdict(list)
        
        flow_to_list_of_things_in_the_same_direction : Dict[Var, List[Var]] = defaultdict(list)
        
        for node in nodes:
            for direction in DIRECTIONS:
                end_node = (node[0] + direction[0], node[1] + direction[1])
                
                # skip if end node is out of bounds
                if end_node[0] < 0 or end_node[0] >= width or end_node[1] < 0 or end_node[1] >= height:
                    continue
                                        
                # create a variable to represent if a belt is placed at the node
                belt_var_name = f"belt_{node[0]}_{node[1]}_{end_node[0]}_{end_node[1]}"
                belt_var = model.addVar(vtype=GRB.BINARY, name=belt_var_name)
                all_belts.append(belt_var)
                node_belts[node].append(belt_var)
                
                # create a variable to represent the flow of resources from the node to the end node
                flow_var_name = f"flow_{node[0]}_{node[1]}_{end_node[0]}_{end_node[1]}"
                flow_var = model.addVar(vtype=GRB.INTEGER, name=flow_var_name, lb=0, ub=self.BELT_MAX_FLOW)
                all_flows.append(flow_var)
                node_flow_out[node].append(flow_var)
                node_flow_in[end_node].append(flow_var)
                
                # model update
                model.update()
                flow_to_list_of_things_in_the_same_direction[flow_var].append(belt_var)
                
                # create extractor platform if node is in the list of nodes to extract
                if node in nodes_to_extract:
                    # create a variable to represent if a miner is placed at the node
                    miner_var_name = f"miner_{node[0]}_{node[1]}_{end_node[0]}_{end_node[1]}"
                    miner_var = model.addVar(vtype=GRB.BINARY, name=miner_var_name)
                    all_miner_platforms.append(miner_var)
                    node_miners[node].append(miner_var)
                    
                    flow_to_list_of_things_in_the_same_direction[flow_var].append(miner_var)
                    
                    # create a variable to represent if a extender platform is placed at the node
                    var_name = f"extender_{node[0]}_{node[1]}_{end_node[0]}_{end_node[1]}"
                    extender_var = model.addVar(vtype=GRB.BINARY, name=var_name)
                    all_extender_platforms.append(extender_var)
                    node_extenders[node].append(extender_var)
                    
                    flow_to_list_of_things_in_the_same_direction[flow_var].append(extender_var)
                    
            
        # ----------------------------------------------------------
        # set objective of the problem
        # ----------------------------------------------------------
                    
        # set first objective to maximize the number of extractors used
        # set second objective to minimize the number of belts used
        model.setObjectiveN(quicksum(all_miner_platforms + all_extender_platforms), index=0, priority=1, name="maximize_extractors", weight=-1.0)
        model.setObjectiveN(quicksum(all_belts), index=1, priority=0, name="minimize_belts", weight=1.0)
        
        # ----------------------------------------------------------
        # add constraints for the problem
        # ----------------------------------------------------------
        
        # create - is_node_used_by_belt
        node_used_by_belt : Dict[Tuple[int, int], Var] = {}
        for node in nodes:
            var_name = f"node_used_by_belt_{node[0]}_{node[1]}"
            constr_name = f"node_used_by_belt_constr_{node[0]}_{node[1]}"
            node_used_by_belt_var = model.addVar(vtype=GRB.BINARY, name=var_name)
            node_used_by_belt[node] = node_used_by_belt_var
            model.addGenConstrOr(node_used_by_belt_var, [belt for belt in node_belts.get(node, [])], name=constr_name)
        
        # constraint - XOR(belt, extender, miner)
        for node in nodes:
            # add constraint that only one thing can be at the node
            sum_of_things = quicksum([node_used_by_belt.get(node, 0)] + node_extenders.get(node, []) + node_miners.get(node, []))
            constr_name = f"only_one_thing_at_node_{node[0]}_{node[1]}"
            model.addConstr(sum_of_things <= 1, name=constr_name)
        
        # create - is_node_used_by_extractor
        node_used_by_extractor : Dict[Tuple[int, int], Var] = {}
        for node in nodes:
            var_name = f"node_used_by_extractor_{node[0]}_{node[1]}"
            constr_name = f"node_used_by_extractor_constr_{node[0]}_{node[1]}"
            node_used_by_extractor_var = model.addVar(vtype=GRB.BINARY, name=var_name)
            node_used_by_extractor[node] = node_used_by_extractor_var
            model.addGenConstrOr(node_used_by_extractor_var, [miner for miner in node_miners.get(node, [])] + [extender for extender in node_extenders.get(node, [])], name=constr_name)
        
        # create - is node used by nothing
        node_used_by_something : Dict[Tuple[int, int], Var] = {}
        for node in nodes:
            var_name = f"node_used_by_something_{node[0]}_{node[1]}"
            constr_name = f"node_used_by_something_constr_{node[0]}_{node[1]}"
            node_used_by_something_var = model.addVar(vtype=GRB.BINARY, name=var_name)
            node_used_by_something[node] = node_used_by_something_var
            model.addGenConstrOr(node_used_by_something_var, [node_used_by_belt[node], node_used_by_extractor[node]], name=constr_name)
        
        # constraint - flow input and output
        for node in nodes:
            # used by belt (in = out)
            model.addGenConstrIndicator(
                node_used_by_belt[node],
                True,
                quicksum(node_flow_out[node]) - quicksum(node_flow_in[node]),
                GRB.EQUAL,
                0.0,
                name=f"extractor_out_flow_{node[0]}_{node[1]}"
            )
            
            # used by extractor (out = in + 1)
            model.addGenConstrIndicator(
                node_used_by_extractor[node],
                True,
                quicksum(node_flow_out[node]) - quicksum(node_flow_in[node]),
                GRB.EQUAL,
                1.0,
                name=f"passthrough_out_flow_{node[0]}_{node[1]}"
            )
            
            # skip the last condition if the node is in sink nodes
            if node in nodes_sink:
                continue
            
            # not used by something (in = out = 0)
            model.addGenConstrIndicator(
                node_used_by_something[node],
                False,
                quicksum(node_flow_out[node]),
                GRB.EQUAL,
                0.0,
                name=f"nothing_out_flow_{node[0]}_{node[1]}"
            )
            model.addGenConstrIndicator(
                node_used_by_something[node],
                False,
                quicksum(node_flow_in[node]),
                GRB.EQUAL,
                0.0,
                name=f"nothing_in_flow_{node[0]}_{node[1]}"
            )
        
        # constraint - max flow
        for node in nodes:
            # extractor - 4
            model.addGenConstrIndicator(
                node_used_by_extractor[node],
                True,
                quicksum(node_flow_out[node]),
                GRB.LESS_EQUAL,
                4.0,
                name=f"extractor_flow_cap_{node[0]}_{node[1]}"
            )
            
            # belt - 12
            model.addGenConstrIndicator(
                node_used_by_belt[node],
                True,
                quicksum(node_flow_out[node]),
                GRB.LESS_EQUAL,
                self.BELT_MAX_FLOW,
                name=f"belt_flow_cap_{node[0]}_{node[1]}"
            )
            
        # create - flow greater than zero
        flow_greater_than_zero : Dict[Var, Var] = {}
        for flow in all_flows:
            var_name = f"flow_greater_than_zero_{flow.varName}"
            constr_name = f"flow_greater_than_zero_constr_{flow.varName}"
            flow_greater_than_zero_var = model.addVar(vtype=GRB.BINARY, name=var_name)
            flow_greater_than_zero[flow] = flow_greater_than_zero_var
            model.addGenConstrIndicator(flow_greater_than_zero_var, True, flow, GRB.GREATER_EQUAL, 1.0, name=constr_name)
            model.addGenConstrIndicator(flow_greater_than_zero_var, False, flow, GRB.EQUAL, 0.0, name=constr_name + "_zero")
            
            
        # if have flow value, something must be in the same direction
        for outflow in all_flows:        
            # get the list of things in the same direction
            flow_greater_than_zero_var = flow_greater_than_zero.get(outflow, None)
            things_in_flow_direction = flow_to_list_of_things_in_the_same_direction.get(outflow, [])
            
            # add the constraint only if flow_greater_than_zero_var is not None
            if flow_greater_than_zero_var is not None:
                model.addGenConstrIndicator(
                    flow_greater_than_zero_var,
                    True,
                    quicksum(things_in_flow_direction),
                    GRB.GREATER_EQUAL,
                    1.0,
                    name=f"flow_direction_{outflow.varName}"
                )
                
        # if extender is true, the end node must have extender or miner
        for extender in all_extender_platforms:
            # get the start and end nodes of the extender
            var_parts = extender.varName.split('_')
            start_node = (int(var_parts[1]), int(var_parts[2]))
            end_node = (int(var_parts[3]), int(var_parts[4]))
            
            # add the constraint
            model.addGenConstrIndicator(
                extender,
                True,
                node_used_by_extractor[end_node],
                GRB.EQUAL,
                1.0,
                name=f"extender_end_node_{start_node[0]}_{start_node[1]}_{end_node[0]}_{end_node[1]}"
            )
        
        # if miner is true, the end node must have belt
        for miner in all_miner_platforms:
            # get the start and end nodes of the miner
            var_parts = miner.varName.split('_')
            start_node = (int(var_parts[1]), int(var_parts[2]))
            end_node = (int(var_parts[3]), int(var_parts[4]))
            
            # add the constraint
            model.addGenConstrIndicator(
                miner,
                True,
                node_used_by_belt[end_node],
                GRB.EQUAL,
                1.0,
                name=f"miner_end_node_{start_node[0]}_{start_node[1]}_{end_node[0]}_{end_node[1]}"
            )
        
        # if belt is true, the end node must not have extractor
        for belt in all_belts:
            # get the start and end nodes of the belt
            var_parts = belt.varName.split('_')
            start_node = (int(var_parts[1]), int(var_parts[2]))
            end_node = (int(var_parts[3]), int(var_parts[4]))
            
            # add the constraint
            model.addGenConstrIndicator(
                belt,
                True,
                node_used_by_extractor[end_node],
                GRB.EQUAL,
                0.0,
                name=f"belt_end_node_{start_node[0]}_{start_node[1]}_{end_node[0]}_{end_node[1]}"
            )
        
        # ----------------------------------------------------
        # store the model
        # ----------------------------------------------------
        self.model = model
        self.all_extender_platforms = all_extender_platforms
        self.all_miner_platforms = all_miner_platforms
        self.all_belts = all_belts
        self.nodes_to_extract = nodes_to_extract
        self.nodes_sink = nodes_sink
        self.node_flow_in = node_flow_in        
        
    def run_solver(self, miner_timelimit = 5, belt_timelimit = 5, belt_gap = 0.05) -> None:
        # set limits
        optimize_miner = self.model.getMultiobjEnv(0)
        optimize_miner.setParam('TimeLimit', miner_timelimit)
        optimize_belts = self.model.getMultiobjEnv(1)
        optimize_belts.setParam('MIPGap', belt_gap)
        optimize_belts.setParam('TimeLimit', belt_timelimit)
        
        # optimize the model
        self.model.optimize()
        
        # store solution
        self.all_miner_platforms_sol = [FakeVar(VarName=miner.VarName, X=miner.X) for miner in self.all_miner_platforms]
        self.all_extender_platforms_sol = [FakeVar(VarName=extender.VarName, X=extender.X) for extender in self.all_extender_platforms]
        self.all_belts_sol = [FakeVar(VarName=belt.VarName, X=belt.X) for belt in self.all_belts]
        self.nodes_to_extract_sol = self.nodes_to_extract
        self.node_flow_in_sol = {node: [FakeVar(VarName=flow.VarName, X=flow.X) for flow in flows] for node, flows in self.node_flow_in.items()}
                
    def save_variables(self, filename: str) -> None:
        # save the variables to a file
        var_to_txt(filename, self.all_extender_platforms, self.all_miner_platforms, self.all_belts)
        
    def get_solution_blueprint(self, miner_blueprint: Optional[str] = None) -> str:
        if miner_blueprint is None:
            # use the default blueprint if none is provided
            miner_blueprint = self.default_blueprint
        
        # generate blueprint
        return compose_blueprint(self.all_miner_platforms, self.all_extender_platforms, self.all_belts, miner_blueprint=miner_blueprint)
    
    def get_solution_image(self) -> BytesIO:
        # render the result
        blob = render_result(
            self.all_miner_platforms_sol,
            self.all_extender_platforms_sol,
            self.all_belts_sol,
            nodes_to_extract=self.nodes_to_extract,
            nodes_sink=self.nodes_sink,
            node_flow_in=self.node_flow_in_sol)
        
        # return the blob
        return blob
    
    def show_solution_image(self) -> None:
        # render the result
        blob = render_result(
            self.all_miner_platforms_sol,
            self.all_extender_platforms_sol,
            self.all_belts_sol,
            nodes_to_extract=self.nodes_to_extract,
            nodes_sink=self.nodes_sink,
            node_flow_in=self.node_flow_in_sol)
        
        # show in cv2 window
        cv2.imshow("Astroid Miner Solution", cv2.imdecode(np.frombuffer(blob.getvalue(), np.uint8), cv2.IMREAD_COLOR))
        cv2.waitKey(0)

def render_result(all_miner_platforms: List[FakeVar],
                  all_extender_platforms: List[FakeVar],
                  all_belts: List[FakeVar],
                  nodes_to_extract: List[Tuple[int, int]] = [],
                  nodes_sink: List[Tuple[int, int]] = [],
                  node_flow_in: Dict[Tuple[int, int], List[FakeVar]] = defaultdict(list)) -> BytesIO:
    
    # -------------------------------------------
    # settings
    # -------------------------------------------
    
    # colors
    edge_color = 'black'
    belt_color = 'blue'
    miner_color = 'green'
    miner_belt_color = belt_color
    extender_color = 'orange'
    extender_belt_color = 'black'
    
    # from all_belts, extract all nodes
    all_nodes = set()
    for belt in all_belts:
        node = tuple(map(int, belt.VarName.split('_')[1:3]))
        all_nodes.add(node)
    
    # compute x and y limits
    x_min = min(node[0] for node in all_nodes)
    x_max = max(node[0] for node in all_nodes)
    y_min = min(node[1] for node in all_nodes)
    y_max = max(node[1] for node in all_nodes)
    
    # compute number of miners
    num_miners = sum(1 for miner in all_miner_platforms if miner.X > 0.5)
    num_extenders = sum(1 for extender in all_extender_platforms if extender.X > 0.5)
    num_belts = sum(1 for belt in all_belts if belt.X > 0.5)
    
    # initialize plt
    plt.clf()
    plt.xlim(x_min - 1, x_max + 1)
    plt.ylim(y_min - 1, y_max + 1)
    # plt.grid(True)
    plt.xticks(range(x_min - 1, x_max + 2))
    plt.yticks(range(y_min - 1, y_max + 2))
    plt.gca().set_aspect('equal', adjustable='box')
    # include first optimization objective in the title
    plt.title("Asteroid Miner Solution = " + str(num_miners) + " miners, " + str(num_extenders) + " extenders, " + str(num_belts) + " belts")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    # plt.axhline(0, color='black', lw=0.5)
    # plt.axvline(0, color='black', lw=0.5)
    
    # draw nodes to extract
    plt.scatter(*zip(*nodes_to_extract), color='lightgrey', s=150, marker='s', zorder = 0)
    
    # draw sink nodes
    plt.scatter(*zip(*nodes_sink), color='red', s=50, marker='x', zorder = 2)
    
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
            
    # draw sink nodes with flow value
    for node in nodes_sink:
        # get flow value
        flow_value = sum(flow.X for flow in node_flow_in[node])
        
        # skip if value is zero
        if flow_value == 0:
            continue
        
        # put text
        plt.text(node[0], node[1], f"{flow_value:.0f}", fontsize=10, ha='center', va='bottom', color='black', zorder=3)
    
    # add legend
    plt.legend()
    plt.tight_layout()
        
    # return the figure as a PNG image blob
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    
    # return
    return buffer
    
if __name__ == "__main__":
    # read input png
    path = Path("images/example3.png")
    astroid_location = astroid_parser(path, 0.5)    
    
    # return if none
    if astroid_location is None:
        print("No astroid location found.")
        exit(0)
    
    # created by ET01
    MINER_BLUEPRINT = "SHAPEZ2-2-H4sIAN0dd2cA/6xaXW+bMBT9L9Ye0YTNl0Haw7J2UrVEqtqs2jRVE0qcDo1C5JBtUZX/PhIMNRCofU37ELXhnHt8fX2uDbygBxRhbHsWmt2i6AW9Kw5bhiJ0s0vjbI0sdLPKs9MXV3ERo+gHSsq/o+rb2zResWeWFeVl53+n8SHfF+/n54+f97/iLVskGePIyvZpKi66ft4WB/R4tNB1VvCE7UrWF7QsY17AoZksarZP0nWSPQ3JKgUVm5w/70TAKuruxBfd7avfXuRvKPIt9B1FZQ7uUORYZy3X/woer4qcX7FNvE+Lm6xgPIvTh5gncTnio3VGBmAklZBYCxmCkZVaV1Y7Y2khQHO26QIXCec5Z+uawO8TzJNNgb9uFcBN9HmjW4r+Oed/Y74ezRYMizF4kgRUccA9sbXM25wX9yxbM95FWOhTec2Xj+efD01Y5xLDHVux5M8QRwl/xRNwiYjQIKgLz7MrD3jB+BPjZJnj+Rslhb1uotRrWWBbI9WsR38Aq7wYKgKiGdwfxY4UpqgLA9liQcB0Y9sAHPalD9dJp5p90BxXEQOD+jiFV7XadmEIJKwyBsEqE2ybxA8vDFt9NQs0GUia0tBdcFsEQakMdQBtHAQVgj31ddzJUgv5dkN7jQdu3UCw8BvQ3NRYxcF2q/FVt2Eb71Jo93FQjdTBXXg7hmXdbQ1awaO9XpYUOpl3YXTqVUXA9lwXFcwf60lxYLK9AYPULkxPam0OuDq9CQbT2gxUxbI8HwDHywuy+XEN+rlQS1smMotXv8cwbo2pjA8oOJTwGLBGQpjx+ibgRjlcM1AtRCeVdd5v06Qor8bL3BlfxVSe0lNJkNEmKlBVRgkgNW4bD6lfINg3ARNp2RG4ZwXDNBqW5Yx6gPIdkEDzGEJk4zZOwmUe7SwMbrTf3j8S2AZfoLHBBp+C7Nsf9SOlg4Wt3KICeZRYp2METajG8R34zYVasoKjBVJ+nJah6SiGm1otVXsrZMOsTB/ndqYGqhbeiqFotzNFBsqJkXICOzja5gcwG+qUdCDzBkL6REA5ZCo54D4SNizgu2sYq+/8bbn3aPlqDcWmxioRqe4VbTlJWt7aVg0xV9xSC6oU/yKFxl4Dd1I/gRKTJdTWQ6bSA9+LBfLBUkXI4qkjJOiefYAMOk47RIGNKahuoQznYxIeffMfyc0kRFS3dEczRKbKEJkqQwZEocEZITQ4IwirvnCrRqtBUcnpTfpTaw2pN6mg3x7P8q/yv5nyAIBNiho7MTVsCXSiDkUnaVB0ov5EDduT3X7xAvxM0O0vDYU9X/Oqy8gdUMXHxoYMgQFDvZHzjLPYonA004jd0e2v6pNdUwpiToHNKWxjitCYoeUUo9P4aKFZksX88MD4Ljm9+XZ6Z+94fDwe/wsgwABYhMLTwicAAA==$"
    
    optimizer = AstroidSolver()
    optimizer.add_astroid_locations(astroid_location)
    optimizer.run_solver()
    optimizer.save_variables("variables.txt")
    blueprint = optimizer.get_solution_blueprint(MINER_BLUEPRINT)
    print(blueprint)
    optimizer.show_solution_image()