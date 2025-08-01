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
from app.astroid_parser import astroid_parser
from app.var_to_txt import var_to_txt, FakeVar
from app.blueprint_composer import compose_blueprint
from app.astroid_parser import get_brush_blueprint, parse_using_blueprint

DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

class AstroidSolver:
    def __init__(self):
        # general settings
        self.BELT_MAX_FLOW = 12 * 4
        
        # default blueprint
        self.default_blueprint = "SHAPEZ2-2-H4sIAN0dd2cA/6xaXW+bMBT9L9Ye0YTNl0Haw7J2UrVEqtqs2jRVE0qcDo1C5JBtUZX/PhIMNRCofU37ELXhnHt8fX2uDbygBxRhbHsWmt2i6AW9Kw5bhiJ0s0vjbI0sdLPKs9MXV3ERo+gHSsq/o+rb2zResWeWFeVl53+n8SHfF+/n54+f97/iLVskGePIyvZpKi66ft4WB/R4tNB1VvCE7UrWF7QsY17AoZksarZP0nWSPQ3JKgUVm5w/70TAKuruxBfd7avfXuRvKPIt9B1FZQ7uUORYZy3X/woer4qcX7FNvE+Lm6xgPIvTh5gncTnio3VGBmAklZBYCxmCkZVaV1Y7Y2khQHO26QIXCec5Z+uawO8TzJNNgb9uFcBN9HmjW4r+Oed/Y74ezRYMizF4kgRUccA9sbXM25wX9yxbM95FWOhTec2Xj+efD01Y5xLDHVux5M8QRwl/xRNwiYjQIKgLz7MrD3jB+BPjZJnj+Rslhb1uotRrWWBbI9WsR38Aq7wYKgKiGdwfxY4UpqgLA9liQcB0Y9sAHPalD9dJp5p90BxXEQOD+jiFV7XadmEIJKwyBsEqE2ybxA8vDFt9NQs0GUia0tBdcFsEQakMdQBtHAQVgj31ddzJUgv5dkN7jQdu3UCw8BvQ3NRYxcF2q/FVt2Eb71Jo93FQjdTBXXg7hmXdbQ1awaO9XpYUOpl3YXTqVUXA9lwXFcwf60lxYLK9AYPULkxPam0OuDq9CQbT2gxUxbI8HwDHywuy+XEN+rlQS1smMotXv8cwbo2pjA8oOJTwGLBGQpjx+ibgRjlcM1AtRCeVdd5v06Qor8bL3BlfxVSe0lNJkNEmKlBVRgkgNW4bD6lfINg3ARNp2RG4ZwXDNBqW5Yx6gPIdkEDzGEJk4zZOwmUe7SwMbrTf3j8S2AZfoLHBBp+C7Nsf9SOlg4Wt3KICeZRYp2METajG8R34zYVasoKjBVJ+nJah6SiGm1otVXsrZMOsTB/ndqYGqhbeiqFotzNFBsqJkXICOzja5gcwG+qUdCDzBkL6REA5ZCo54D4SNizgu2sYq+/8bbn3aPlqDcWmxioRqe4VbTlJWt7aVg0xV9xSC6oU/yKFxl4Dd1I/gRKTJdTWQ6bSA9+LBfLBUkXI4qkjJOiefYAMOk47RIGNKahuoQznYxIeffMfyc0kRFS3dEczRKbKEJkqQwZEocEZITQ4IwirvnCrRqtBUcnpTfpTaw2pN6mg3x7P8q/yv5nyAIBNiho7MTVsCXSiDkUnaVB0ov5EDduT3X7xAvxM0O0vDYU9X/Oqy8gdUMXHxoYMgQFDvZHzjLPYonA004jd0e2v6pNdUwpiToHNKWxjitCYoeUUo9P4aKFZksX88MD4Ljm9+XZ6Z+94fDwe/wsgwABYhMLTwicAAA==$"
        
        # solution flag
        self.has_solution = False

    def add_astroid_locations(self, astroid_location: np.ndarray) -> None:        
        # list of all nodes (the box around asteroid location and a border of 1 around it as sinks)
        x_min = min(x for x, y in astroid_location) - 1
        x_max = max(x for x, y in astroid_location) + 1
        y_min = min(y for x, y in astroid_location) - 1
        y_max = max(y for x, y in astroid_location) + 1
        nodes = [(x, y) for x in range(x_min, x_max + 1) for y in range(y_min, y_max + 1)]
        
        # list of source nodes
        nodes_to_extract = [(x, y) for x, y in astroid_location]
        
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
        node_used_by_elevator : Dict[Tuple[int, int], Var] = {}
        
        flow_to_list_of_things_in_the_same_direction : Dict[Var, List[Var]] = defaultdict(list)
        
        for node in nodes_to_extract:            
            for direction in DIRECTIONS:
                end_node = (node[0] + direction[0], node[1] + direction[1])
                
                # skip if end node is out of bounds
                if end_node[0] < x_min or end_node[0] > x_max or end_node[1] < y_min or end_node[1] > y_max:
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
        model.update()
        
        # node_used_by_elevator
        for node in nodes:
            if node in nodes_to_extract:
                # create a variable to represent if an elevator is placed at the node
                elevator_var_name = f"elevator_{node[0]}_{node[1]}"
                elevator_var = model.addVar(vtype=GRB.BINARY, name=elevator_var_name)
                node_used_by_elevator[node] = elevator_var
            else:
                # create a dummy variable for elevator if node is not in nodes_to_extract
                elevator_var = model.addVar(vtype=GRB.BINARY, name=f"dummyelevator_{node[0]}_{node[1]}")
                model.addConstr(elevator_var == 0, name=f"dummyelevator_constr_{node[0]}_{node[1]}")
                node_used_by_elevator[node] = elevator_var
        
        # node is miner
        node_used_by_miner : Dict[Tuple[int, int], Var] = model.addVars(nodes, vtype=GRB.BINARY, name="node_used_by_miner")
        for node in nodes:
            model.addGenConstrOr(node_used_by_miner[node], node_miners.get(node, []), name=f"node_used_by_miner_constr_{node}")
                
        # node is miner and is saturated
        node_is_miner_and_flow_is = model.addVars(nodes, [1, 2, 3, 4], vtype=GRB.BINARY, name="node_is_miner_and_flow_is")
        for node in nodes:
            for k in [1, 2, 3, 4]:
                # make sure node is miner
                model.addConstr(
                    node_is_miner_and_flow_is[node[0], node[1], k] <= node_used_by_miner[node],
                    name=f"node_is_miner_and_flow_is_{node}_{k}_constr"
                )
                
                # make sure flow is k
                model.addGenConstrIndicator(
                    node_is_miner_and_flow_is[node[0], node[1], k],
                    True,
                    quicksum(node_flow_out[node]),
                    GRB.EQUAL,
                    k,
                    name=f"node_is_miner_and_flow_is_{node}_{k}"
                )
        
        # encourage more saturated miners
        more_saturated_miner_objective = quicksum(
            1000000 * node_is_miner_and_flow_is[n[0], n[1], 4] +
            10000 * node_is_miner_and_flow_is[n[0], n[1], 3] +
            100 * node_is_miner_and_flow_is[n[0], n[1], 2] +
            1 * node_is_miner_and_flow_is[n[0], n[1], 1] 
            for n in nodes)
                            
        # ----------------------------------------------------------
        # set objective of the problem
        # ----------------------------------------------------------
                    
        # set first objective to maximize the number of extractors used
        # set second objective to minimize the number of belts used
        model.setObjectiveN(quicksum(all_miner_platforms+all_extender_platforms), index=0, priority=2, name="maximize_extractors", weight=-1.0)
        model.setObjectiveN(more_saturated_miner_objective, index=1, priority=1, name="maximize_saturated_miners", weight=-1.0)
        
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
        
        # create - is_node_used_by_extractor
        node_used_by_extractor : Dict[Tuple[int, int], Var] = {}
        for node in nodes:
            var_name = f"node_used_by_extractor_{node[0]}_{node[1]}"
            constr_name = f"node_used_by_extractor_constr_{node[0]}_{node[1]}"
            node_used_by_extractor_var = model.addVar(vtype=GRB.BINARY, name=var_name)
            node_used_by_extractor[node] = node_used_by_extractor_var
            model.addGenConstrOr(node_used_by_extractor_var, [miner for miner in node_miners.get(node, [])] + [extender for extender in node_extenders.get(node, [])], name=constr_name)
        
        # create - is node used by something
        node_used_by_something : Dict[Tuple[int, int], Var] = {}
        for node in nodes:
            var_name = f"node_used_by_something_{node[0]}_{node[1]}"
            constr_name = f"node_used_by_something_constr_{node[0]}_{node[1]}"
            node_used_by_something_var = model.addVar(vtype=GRB.BINARY, name=var_name)
            node_used_by_something[node] = node_used_by_something_var
            model.addGenConstrOr(node_used_by_something_var, [node_used_by_belt[node], node_used_by_extractor[node], node_used_by_elevator[node]], name=constr_name)
        
        # constraint - XOR(belt, extender, miner, elevator)
        for node in nodes:
            # add constraint that only one thing can be at the node
            sum_of_things = quicksum([node_used_by_belt.get(node, 0)] + node_extenders.get(node, []) + node_miners.get(node, []) + [node_used_by_elevator.get(node, 0)])
            constr_name = f"only_one_thing_at_node_{node[0]}_{node[1]}"
            model.addConstr(sum_of_things <= 1, name=constr_name)
        
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
            
            # used by elevator, no out flow
            model.addGenConstrIndicator(
                node_used_by_elevator[node],
                True,
                quicksum(node_flow_out[node]),
                GRB.EQUAL,
                0.0,
                name=f"elevator_out_flow_{node[0]}_{node[1]}"
            )
            
            # if node is in nodes to extract and has nothing in it, should have zero out flow and zero in flow
            if node in nodes_to_extract:
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
            
            # belt - self.BELT_MAX_FLOW
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
                
        # if miner is true, the end node must not be used by extractor
        for miner in all_miner_platforms:
            # get the start and end nodes of the miner
            var_parts = miner.varName.split('_')
            start_node = (int(var_parts[1]), int(var_parts[2]))
            end_node = (int(var_parts[3]), int(var_parts[4]))
            
            # add the constraint
            model.addGenConstrIndicator(
                miner,
                True,
                node_used_by_extractor[end_node],
                GRB.EQUAL,
                0.0,
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
        
        # if node is elevator, only one in flow direction is allowed
        for node in nodes_to_extract:
            # add the constraint
            model.addGenConstrIndicator(
                node_used_by_elevator[node],
                True,
                quicksum(flow_greater_than_zero[flow] for flow in node_flow_in[node]),
                GRB.LESS_EQUAL,
                1.0,
                name=f"elevator_in_flow_{node[0]}_{node[1]}"
            )
        
        # ----------------------------------------------------
        # store the model
        # ----------------------------------------------------
        self.model = model
        self.all_extender_platforms = all_extender_platforms
        self.all_miner_platforms = all_miner_platforms
        self.all_belts = all_belts
        self.nodes_to_extract = nodes_to_extract
        self.node_flow_in = node_flow_in   
        self.node_flow_out = node_flow_out
        self.node_used_by_elevator = node_used_by_elevator     
        
    def run_solver(self, miners_timelimit : float = 5.0, saturation_timelimit : float = 5.0, with_elevator : bool = False) -> None:
        # set limits
        optimize_extractors = self.model.getMultiobjEnv(0)
        optimize_extractors.setParam('TimeLimit', miners_timelimit)
        optimize_saturation = self.model.getMultiobjEnv(1)
        optimize_saturation.setParam('TimeLimit', saturation_timelimit)
        
        if not with_elevator:
            # if not with elevator, set the elevator variables to zero
            for node in self.nodes_to_extract:
                self.model.addConstr(self.node_used_by_elevator[node] == 0, name=f"elevator_zero_{node[0]}_{node[1]}")
        
        # optimize the model
        self.model.optimize()
        
        # store solution
        self.all_miner_platforms_sol = [FakeVar(VarName=miner.VarName, X=miner.X) for miner in self.all_miner_platforms]
        self.all_extender_platforms_sol = [FakeVar(VarName=extender.VarName, X=extender.X) for extender in self.all_extender_platforms]
        self.all_belts_sol = [FakeVar(VarName=belt.VarName, X=belt.X) for belt in self.all_belts]
        self.nodes_to_extract_sol = self.nodes_to_extract
        self.node_flow_in_sol = {node: [FakeVar(VarName=flow.VarName, X=flow.X) for flow in flows] for node, flows in self.node_flow_in.items()}
        self.node_flow_out_sol = {node: [FakeVar(VarName=flow.VarName, X=flow.X) for flow in flows] for node, flows in self.node_flow_out.items()}
        self.node_used_by_elevator_sol = {node: FakeVar(VarName=elevator.VarName, X=elevator.X) for node, elevator in self.node_used_by_elevator.items()}
        self.all_elevators_sol = [FakeVar(VarName=elevator.VarName, X=elevator.X) for elevator in self.node_used_by_elevator.values()]

        self.has_solution = True
                
    def save_variables(self, filename: str) -> None:
        # save the variables to a file
        var_to_txt(filename, self.all_extender_platforms, self.all_miner_platforms, self.all_belts)
        
    def get_solution_blueprint(self, miner_blueprint: Optional[str] = None, remove_non_saturated_miners: bool = False) -> str:
        if miner_blueprint is None:
            # use the default blueprint if none is provided
            miner_blueprint = self.default_blueprint
        
        # skip if no solution
        if not self.has_solution:
            return "Solution not found"
        
        if remove_non_saturated_miners:
            miner_platforms_sol, extender_platforms_sol = remove_non_saturated_miners_func(self.all_miner_platforms_sol, self.all_extender_platforms_sol)
        else:
            miner_platforms_sol = self.all_miner_platforms_sol
            extender_platforms_sol = self.all_extender_platforms_sol

        # generate blueprint
        return compose_blueprint(miner_platforms_sol, extender_platforms_sol, self.all_belts_sol, self.all_elevators_sol, miner_blueprint=miner_blueprint)
    
    def get_solution_image(self, remove_non_saturated_miners: bool = False) -> BytesIO:
        # render the result
        if remove_non_saturated_miners:
            miner_platforms_sol, extender_platforms_sol = remove_non_saturated_miners_func(self.all_miner_platforms_sol, self.all_extender_platforms_sol)
        else:
            miner_platforms_sol = self.all_miner_platforms_sol
            extender_platforms_sol = self.all_extender_platforms_sol
        
        blob = render_result(
            miner_platforms_sol,
            extender_platforms_sol,
            self.all_belts_sol,
            nodes_to_extract=self.nodes_to_extract,
            node_flow_in=self.node_flow_in_sol,
            node_flow_out=self.node_flow_out_sol,
            node_used_by_elevator=self.node_used_by_elevator_sol)
        
        # return the blob
        return blob
    
    def show_solution_image(self) -> None:
        # render the result
        blob = render_result(
            self.all_miner_platforms_sol,
            self.all_extender_platforms_sol,
            self.all_belts_sol,
            nodes_to_extract=self.nodes_to_extract,
            node_flow_in=self.node_flow_in_sol,
            node_flow_out=self.node_flow_out_sol,
            node_used_by_elevator=self.node_used_by_elevator_sol)
        
        # show in cv2 window
        cv2.imshow("Astroid Miner Solution", cv2.imdecode(np.frombuffer(blob.getvalue(), np.uint8), cv2.IMREAD_COLOR))
        cv2.waitKey(0)

def remove_non_saturated_miners_func(all_miner_platforms_sol: List[FakeVar], all_extender_platforms_sol: List[FakeVar]):    
    # miner nodes
    miner_nodes = []
    for miner in all_miner_platforms_sol:
        # skip if not used
        if miner.X < 0.5:
            continue
        var_parts = miner.VarName.split('_')
        start_node = (int(var_parts[1]), int(var_parts[2]))
        miner_nodes.append(start_node)
    
    # extension map
    extension_maps = {}
    for extender in all_extender_platforms_sol:
        # skip if extender is not used
        if extender.X < 0.5:
            continue
        var_parts = extender.VarName.split('_')
        start_node = (int(var_parts[1]), int(var_parts[2]))
        end_node = (int(var_parts[3]), int(var_parts[4]))
        extension_maps[start_node] = end_node
    for start_node, end_node in extension_maps.items():
        # similar to union find, compress the path
        while end_node in extension_maps:
            end_node = extension_maps[end_node]
        extension_maps[start_node] = end_node

    # miner to extension count
    miner_to_extension_count = {}
    for miner_node in miner_nodes:
        count = sum(1 for start_node, end_node in extension_maps.items() if end_node == miner_node)
        miner_to_extension_count[miner_node] = count
    
    # remove non-saturated miners and extensions
    miners_not_saturated = [miner_node for miner_node in miner_nodes if miner_to_extension_count[miner_node] < 3]
    extension_not_saturated = [start_node for start_node, end_node in extension_maps.items() if end_node in miners_not_saturated]
    all_miner_platforms_sol_new = []
    all_extender_platforms_sol_new = []
    for miner in all_miner_platforms_sol:
        start_node = (int(miner.VarName.split('_')[1]), int(miner.VarName.split('_')[2]))
        if start_node not in miners_not_saturated:
            all_miner_platforms_sol_new.append(miner)
    for extender in all_extender_platforms_sol:
        start_node = (int(extender.VarName.split('_')[1]), int(extender.VarName.split('_')[2]))
        end_node = (int(extender.VarName.split('_')[3]), int(extender.VarName.split('_')[4]))
        if start_node not in extension_not_saturated:
            all_extender_platforms_sol_new.append(extender)
    
    # return the new solution
    return all_miner_platforms_sol_new, all_extender_platforms_sol_new

def render_result(all_miner_platforms: List[FakeVar],
                  all_extender_platforms: List[FakeVar],
                  all_belts: List[FakeVar],
                  nodes_to_extract: List[Tuple[int, int]] = [],
                  node_flow_in: Dict[Tuple[int, int], List[FakeVar]] = defaultdict(list),
                  node_flow_out: Dict[Tuple[int, int], List[FakeVar]] = defaultdict(list),
                  node_used_by_elevator: Dict[Tuple[int, int], FakeVar] = {}) -> BytesIO:
    
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
    elevator_color = 'blue'
    
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
    
    # roughly compute figure size based on the limits
    width = (x_max - x_min + 5) / 3
    height = (y_max - y_min + 5) / 3
    
    # initialize plt
    plt.clf()
    plt.figure(figsize=(width, height))
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
        
    # draw elevator nodes
    for node, elevator in node_used_by_elevator.items():
        if elevator.X > 0.5:
            plt.scatter(node[0], node[1], color=elevator_color, marker='x', s=150, zorder=2)
    
    # draw belts
    for belt in all_belts:
        if belt.X > 0.5:  # if the belt is placed
            start_node = tuple(map(int, belt.VarName.split('_')[1:3]))
            end_node = tuple(map(int, belt.VarName.split('_')[3:5]))
            plt.plot([start_node[0], end_node[0]], [start_node[1], end_node[1]], color=belt_color, linewidth=2, zorder = 1)
    
    # draw miners
    used_miner_nodes = set()
    for miner in all_miner_platforms:
        if miner.X > 0.5:  # if the miner is placed
            start_node = tuple(map(int, miner.VarName.split('_')[1:3]))
            end_node = tuple(map(int, miner.VarName.split('_')[3:5]))
            used_miner_nodes.add(start_node)
            
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
    
    # draw flow out values for miner node
    for node, flows in node_flow_out.items():
        if node not in used_miner_nodes:
            continue
        for flow in flows:
            if flow.X > 0.5:  # if the flow is placed
                # get end node
                end_node = tuple(map(int, flow.VarName.split('_')[3:5]))
                
                # get flow value
                flow_value = flow.X
                
                # put text on the flow direction, lean more towards the start node
                mid_x = (node[0] + end_node[0]) / 2
                mid_y = (node[1] + end_node[1]) / 2
                plt.text(mid_x, mid_y, f"{flow_value:.0f}", fontsize=15, ha='center', va='center', color=belt_color, zorder=3)
    
    # add legend
    plt.tight_layout()
        
    # return the figure as a PNG image blob
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    
    # return
    return buffer
    
if __name__ == "__main__":
    # use simple coordinates
    input_miner_blueprint = get_brush_blueprint(10)
    # input_miner_blueprint = "SHAPEZ2-3-H4sIAPxRSGgA/4zaX2tTQRAF8O+y+HgFZ2/u3vY+ij4UFIqKKFJK0IiBmJT8eSgh392U+OKDnR+FhtKT2ZlzzsLu7BzL5zJF1NqV17dlOpYX+8eHRZnKzW41X/8oXbn5vlk//ePNfD8v07eyPP893a7m+5+b7e9d6daH1eryq+x+zR8W04fD5afcnbrydr3fLhe78xeP5UuZXsarrnw9f/Zd+XRe5d38cXPY3398+uL75XqxLafuX2BVYAiQQgXi0tSuL5nNENcjTtcNwEmgMBimhVUiaUMGu7pwobgZ4nrEVcQF4CRQGAzTwiqRNNSgZbARJR1R0hElHVHSESUdLVAYDNPCKpE01AAlTQlpqHxD5Rsq31D5hso3CxQGw7SwSiQNNcBKU+UHVH5A5QdUfkDlB1QeCwiDYVpYJZKGJTSDpcrPLswqriFuQNwMcT3iKuICcBIoDIZpYZWYG2qAkqYO6dFJPTqpRyf16KQendSjk3p0Ei4YBsO0cFEkDTVASVOHVHRSRSdVdFJFJ1V0UkUnVXQSBgqDYTSsEklDDVDS1CGBTgp0UqCTAp0U2q7Rbo02aywQwjAtrBJJQw2elTT1RmqK1A2pDVL9U+FTxZ/9aiShs6Wz3LPiM/ayPYlbHHc4bnDc37i9cXfj5g4KYyhLyeozsox5kzHzBJ4f8PiApwc8PODZAY8OFiYIZbGsPiPLmDcZM0/grQMvHXjnwCsH3jhstSCUpWQrGlnGfCNUJjY2K7BXga0K7FRgo8KSCkJZSlaf5WXMN0JlYmOPE1uc2OHEBif2Ny33IJSlZPUZWZZ9I1QmNj5l4EsGPmTgOwY+YzQKE4SylKw+I8uYtxozsfHFEh8s8b0SnyvxtdJKDEJZSlafkWXMN0JlTOAkAQ4S4BwBjhFcUZgglKVk9RlZA6EyFXHaBodtcNbmmsIEoSwlq29GqPTOi8NaOquVjmrhpBYOav2F/Z+xu9PpjwADAPJbZEgpJwAA$"
    astroid_location = parse_using_blueprint(input_miner_blueprint)
    
    # return if none
    if astroid_location is None:
        print("No astroid location found.")
        exit(0)
    
    # created by ET01
    MINER_BLUEPRINT = "SHAPEZ2-2-H4sIAN0dd2cA/6xaXW+bMBT9L9Ye0YTNl0Haw7J2UrVEqtqs2jRVE0qcDo1C5JBtUZX/PhIMNRCofU37ELXhnHt8fX2uDbygBxRhbHsWmt2i6AW9Kw5bhiJ0s0vjbI0sdLPKs9MXV3ERo+gHSsq/o+rb2zResWeWFeVl53+n8SHfF+/n54+f97/iLVskGePIyvZpKi66ft4WB/R4tNB1VvCE7UrWF7QsY17AoZksarZP0nWSPQ3JKgUVm5w/70TAKuruxBfd7avfXuRvKPIt9B1FZQ7uUORYZy3X/woer4qcX7FNvE+Lm6xgPIvTh5gncTnio3VGBmAklZBYCxmCkZVaV1Y7Y2khQHO26QIXCec5Z+uawO8TzJNNgb9uFcBN9HmjW4r+Oed/Y74ezRYMizF4kgRUccA9sbXM25wX9yxbM95FWOhTec2Xj+efD01Y5xLDHVux5M8QRwl/xRNwiYjQIKgLz7MrD3jB+BPjZJnj+Rslhb1uotRrWWBbI9WsR38Aq7wYKgKiGdwfxY4UpqgLA9liQcB0Y9sAHPalD9dJp5p90BxXEQOD+jiFV7XadmEIJKwyBsEqE2ybxA8vDFt9NQs0GUia0tBdcFsEQakMdQBtHAQVgj31ddzJUgv5dkN7jQdu3UCw8BvQ3NRYxcF2q/FVt2Eb71Jo93FQjdTBXXg7hmXdbQ1awaO9XpYUOpl3YXTqVUXA9lwXFcwf60lxYLK9AYPULkxPam0OuDq9CQbT2gxUxbI8HwDHywuy+XEN+rlQS1smMotXv8cwbo2pjA8oOJTwGLBGQpjx+ibgRjlcM1AtRCeVdd5v06Qor8bL3BlfxVSe0lNJkNEmKlBVRgkgNW4bD6lfINg3ARNp2RG4ZwXDNBqW5Yx6gPIdkEDzGEJk4zZOwmUe7SwMbrTf3j8S2AZfoLHBBp+C7Nsf9SOlg4Wt3KICeZRYp2METajG8R34zYVasoKjBVJ+nJah6SiGm1otVXsrZMOsTB/ndqYGqhbeiqFotzNFBsqJkXICOzja5gcwG+qUdCDzBkL6REA5ZCo54D4SNizgu2sYq+/8bbn3aPlqDcWmxioRqe4VbTlJWt7aVg0xV9xSC6oU/yKFxl4Dd1I/gRKTJdTWQ6bSA9+LBfLBUkXI4qkjJOiefYAMOk47RIGNKahuoQznYxIeffMfyc0kRFS3dEczRKbKEJkqQwZEocEZITQ4IwirvnCrRqtBUcnpTfpTaw2pN6mg3x7P8q/yv5nyAIBNiho7MTVsCXSiDkUnaVB0ov5EDduT3X7xAvxM0O0vDYU9X/Oqy8gdUMXHxoYMgQFDvZHzjLPYonA004jd0e2v6pNdUwpiToHNKWxjitCYoeUUo9P4aKFZksX88MD4Ljm9+XZ6Z+94fDwe/wsgwABYhMLTwicAAA==$"
    
    optimizer = AstroidSolver()
    optimizer.add_astroid_locations(np.array(astroid_location))
    optimizer.run_solver(miners_timelimit = 999.0, saturation_timelimit = 999.0, with_elevator=True)
    optimizer.save_variables("variables.txt")
    blueprint = optimizer.get_solution_blueprint(MINER_BLUEPRINT)
    print(blueprint)
    optimizer.show_solution_image()