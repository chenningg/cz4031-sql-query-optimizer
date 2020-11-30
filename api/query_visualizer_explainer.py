import json
from sys import stderr
import networkx as nx
from networkx.readwrite import json_graph
from custom_errors import *


""" #################################################################### 
Creates a graph, and a text explanation for a given query execution plan
#################################################################### """


def visualize_explain_query(plan):
    try:
        plan = json.loads(plan)
        queue = []
        visited = []

        unique_id = 1

        explanation = ""

        graph = nx.DiGraph()

        if "Plan" in plan:
            root = plan["Plan"]
            root["id"] = string_unique_id(unique_id)
            root["depth"] = 0
            root_node = string_unique_id(unique_id)

            # unique_id = chr(ord(unique_id) + 1)
            unique_id += 1
            # unique_id = get_next_unique_id(unique_id)

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
                children = []

                if "Plans" in curr:
                    depth = curr["depth"] + 1

                    for child in curr["Plans"]:
                        if child not in visited:
                            child["id"] = string_unique_id(unique_id)
                            child["depth"] = depth
                            # unique_id = chr(ord(unique_id) + 1)
                            # unique_id = get_next_unique_id(unique_id)
                            unique_id += 1
                            queue.append(child)
                            children.append(child)

                            graph.add_node(
                                child["id"],
                                node_type=child["Node Type"],
                                cost=child["Startup Cost"] + child["Total Cost"],
                                depth=depth,
                            )

                            graph.add_edge(curr["id"], child["id"])

                    explanation = craft_explanation_string(
                        explanation, curr["Node Type"], children, curr["id"]
                    )

                # If we reach here, we are at a leaf node, add the table itself to the graph
                else:
                    table = {}
                    table["id"] = string_unique_id(unique_id)
                    table["depth"] = curr["depth"] + 1
                    # unique_id = chr(ord(unique_id) + 1)
                    # unique_id = get_next_unique_id(unique_id)
                    unique_id += 1

                    graph.add_node(
                        table["id"],
                        node_type=curr["Relation Name"],
                        cost=0,
                        depth=table["depth"],
                    )

                    graph.add_edge(curr["id"], table["id"])

                    explanation = craft_explanation_string(
                        explanation, curr["Node Type"], curr, curr["id"]
                    )

            # Return graph as JSON
            data = json_graph.node_link_data(graph)

            # Format the explanation to go from leaf to root. We return a list. The last element is an empty string, so pop it first
            explanation = explanation.split(".")
            explanation.pop(-1)
            explanation.reverse()

            return data, explanation
        else:
            return {}
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in visualize_explain_query() - Unable to get the graph and explanation for the query."
        )


""" #################################################################### 
Crafts the explanation string for the graph
#################################################################### """


def craft_explanation_string(explanation, node_type, child_names, curr_name):
    try:
        explanation += node_type + " "

        # Take care of joins and sorts
        if (
            node_type == "Hash"
            or node_type == "Sort"
            or node_type == "Incremental Sort"
            or node_type == "Gather Merge"
            or node_type == "Merge"
            or node_type == "Aggregate"
        ):
            explanation += child_names[0]["id"] + " as " + curr_name + "."
        elif (
            node_type == "Hash Join"
            or node_type == "Nested Loop"
            or node_type == "Merge Join"
        ):

            if node_type == "Nested Loop":
                explanation += "Join "

                explanation += (
                    "between "
                    + child_names[0]["Node Type"]
                    + " "
                    + child_names[0]["id"]
                    + " (outer) and "
                    + child_names[1]["Node Type"]
                    + " "
                    + child_names[1]["id"]
                    + " (inner) as "
                    + curr_name
                    + "."
                )

        else:
            # nodes like Materialize
            try:
                explanation += child_names[0]["id"] + " as " + curr_name + "."
            # Relation nodes
            except:
                explanation += (
                    "on " + child_names["Relation Name"] + " as " + curr_name + "."
                )
        return explanation
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in craft_explanation_string() - Unable to generate text explanation of graph."
        )


""" #################################################################### 
Generates a unique ID (running character sequence) for nodes as a string
#################################################################### """


def string_unique_id(unique_id):
    try:
        return "T" + str(unique_id)
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in string_unique_id() - Unable to generate unique id for QEP nodes."
        )
