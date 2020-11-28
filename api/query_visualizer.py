import json
from sys import stderr
import networkx as nx


def visualize_query(plan):
    try:
        plan = json.loads(plan)

        queue = []
        visited = []

        unique_id = "A"

        graph = nx.Graph()

        if not plan["Plan"]:
            return {}
        else:
            root = plan["Plan"]
            root["id"] = unique_id
            root_node = unique_id
            unique_id += 1

            queue.append(root)

            while queue:
                curr = queue.pop(0)
                visited.append(curr)

                curr_obj = {
                    "node_type": curr["Node Type"],
                    "cost": curr["Startup Cost"] + curr["Total Cost"],
                }

                graph.add_node(curr["id"], curr_obj)

                print(curr["Node Type"], file=stderr)

                if "Plans" in curr:
                    for child in curr["Plans"]:
                        if child not in visited:
                            child["id"] = unique_id
                            unique_id += 1
                            queue.append(child)

                            child_obj = {
                                "node_type": child["Node Type"],
                                "cost": child["Startup Cost"] + child["Total Cost"],
                            }

                            graph.add_node(child["id"], child_obj)
                            graph.add_edge(curr["id"], child["id"])
    except:
        print("Error in query visualizer.", file=stderr)
