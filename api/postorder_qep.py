import json
from sys import stderr

""" #################################################################### 
Prints out a query plan 
#################################################################### """

# Output name of intermediate output
name = 65


def postorder_qep(plan):
    try:
        plan = json.loads(plan)
        plan = plan["Plan"]
        # print(json.dumps(plan, indent=2), file=stderr)

        postorder_result = []

        global name
        name = 65

        def recurse(plan):
            if plan == None:
                return

            global name

            child_names = []

            # My own output name (e.g. A)
            curr_name = ""

            # Recurse all the way down the tree and get the intermediate output(s)
            if plan.get("Plans") != None:
                for branch in plan.get("Plans"):
                    result = recurse(branch)

                    if result:
                        child_names.append(result[0])
                        postorder_result.append(result[1])

                    # If not leaf node, give an arbitrary name
                    curr_name = chr(name)
                    name += 1
            # If we are a leaf node, then just put table name
            else:
                curr_name = plan.get("Relation Name")

            # When we reach here, we can assume we are a leaf node, or that all our children has already recursed.
            output = ""
            node_type = plan.get("Node Type")
            output += node_type + " "

            # Take care of joins and sorts
            if (
                node_type == "Hash"
                or node_type == "Sort"
                or node_type == "Gather Merge"
                or node_type == "Merge"
                or node_type == "Aggregate"
            ):
                output += child_names[0] + " as " + curr_name + "."
            elif (
                node_type == "Hash Join"
                or node_type == "Nested Loop"
                or node_type == "Merge Join"
            ):
                if node_type == "Nested Loop":
                    output += "Join "
                output += (
                    "between "
                    + child_names[0]
                    + " (outer) and "
                    + child_names[1]
                    + " (inner) as "
                    + curr_name
                    + "."
                )
            else:
                output += "on " + curr_name + "."

            # print([curr_name, output], file=stderr)

            return [curr_name, output]

        output = ""
        node_type = plan.get("Node Type")
        result = recurse(plan)

        if result:
            output += node_type + " " + result[0] + " to get final result " + chr(name)

        postorder_result.append(output)

        return postorder_result

    except:
        raise Exception("Error in postorder_qep() - unable to find any nodes in query execution plan.")
