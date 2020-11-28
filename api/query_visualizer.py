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
            root["depth"] = 0
            root_node = unique_id

            unique_id = chr(ord(unique_id) + 1)

            queue.append(root)

            graph.add_node(
                root["id"],
                node_type=root["Node Type"],
                cost=root["Startup Cost"] + root["Total Cost"],
                depth=root["depth"],
            )

            while queue:
                curr = queue.pop(0)
                visited.append(curr)

                if curr["Node Type"] == "Hash":
                    print("================================", file=stderr)
                    print("Plans" in curr, file=stderr)
                    print("HMMMMMMMMMMMMMMMMMMMMMM", file=stderr)
                    print(curr["Plans"], file=stderr)
                    print("================================", file=stderr)

                if "Plans" in curr:
                    depth = curr["depth"] + 1
                    for child in curr["Plans"]:
                        if child not in visited:
                            child["id"] = unique_id
                            child["depth"] = depth
                            unique_id = chr(ord(unique_id) + 1)
                            queue.append(child)

                            graph.add_node(
                                child["id"],
                                node_type=child["Node Type"],
                                cost=child["Startup Cost"] + child["Total Cost"],
                                depth=depth,
                            )

                            graph.add_edge(curr["id"], child["id"])

            # Return graph as JSON
            data = json_graph.node_link_data(graph)
            return data
        else:
            return {}
    except:
        print("Error in query visualizer.", file=stderr)
