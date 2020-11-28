import json
from sys import stderr
import networkx as nx
from networkx.readwrite import json_graph


def visualize_query(plan):
    try:
        plan = json.loads(plan)

        queue = []
        visited = []

        unique_id = "A"

        graph = nx.DiGraph()

        if "Plan" in plan:
            root = plan["Plan"]
            root["id"] = unique_id
            root_node = unique_id

            unique_id = chr(ord(unique_id) + 1)

            queue.append(root)

            while queue:
                curr = queue.pop(0)
                visited.append(curr)

                graph.add_node(
                    curr["id"],
                    node_type=curr["Node Type"],
                    cost=curr["Startup Cost"] + curr["Total Cost"],
                )

                if "Plans" in curr:
                    for child in curr["Plans"]:
                        if child not in visited:
                            child["id"] = unique_id
                            unique_id = chr(ord(unique_id) + 1)
                            queue.append(child)

                            graph.add_node(
                                child["id"],
                                node_type=curr["Node Type"],
                                cost=curr["Startup Cost"] + curr["Total Cost"],
                            )

                            graph.add_edge(curr["id"], child["id"])

            # Return graph as JSON
            data = json_graph.node_link_data(graph)
            return data
        else:
            return {}
    except:
        print("Error in query visualizer.", file=stderr)
