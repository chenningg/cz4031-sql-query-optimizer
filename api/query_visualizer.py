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
                # If we reach here, we are at a leaf node, add the table itself to the graph
                else:
                    table = {}
                    table["id"] = unique_id
                    table["depth"] = depth + 1
                    unique_id = chr(ord(unique_id) + 1)

                    graph.add_node(
                        table["id"],
                        node_type=curr["Relation Name"],
                        cost=0,
                        depth=table["depth"],
                    )

                    graph.add_edge(curr["id"], table["id"])

            # Return graph as JSON
            data = json_graph.node_link_data(graph)
            return data
        else:
            return {}
    except:
        raise Exception("Error in visualize_query() - unable to get the graph for the query")
