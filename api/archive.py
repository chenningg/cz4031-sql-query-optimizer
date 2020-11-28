# """ #################################################################### 
# get the cost of performing scans on relations
# #################################################################### """


# def get_scan_cost(qep_sql_string):
#     # various scan settings. Only enable one (one-hot)
#     scan_types = [
#         "enable_bitmapscan",
#         "enable_indexscan",
#         "enable_seqscan",
#         "enable_tidscan",
#     ]
#     scan_types_qeps = []

#     for scan_type_on in scan_types:
#         scan_type_sql_string = reset_connection_settings_string(
#             "join"
#         )  # make sure joins are all enabled

#         # create the one-hot scan type query
#         for scan_type_inner in scan_types:
#             if scan_type_inner == scan_type_on:
#                 scan_type_sql_string = (
#                     scan_type_sql_string + f"SET {scan_type_inner} = ON;"
#                 )
#             else:
#                 scan_type_sql_string = (
#                     scan_type_sql_string + f"SET {scan_type_inner} = OFF;"
#                 )
#         scan_type_sql_string = scan_type_sql_string + qep_sql_string

#         print(scan_type_sql_string, file=stderr)
#         print("*" * 50, file=stderr)

#         # get the qep for the one-hot scan type
#         scan_type_on_qep = query(scan_type_sql_string, explain=True)
#         scan_type_on_qep = json.dumps(ast.literal_eval(str(scan_type_on_qep)))
#         scan_type_on_qep = json.loads(scan_type_on_qep)

#         scan_types_qeps.append(scan_type_on_qep)

#     # reset the types of scans enabled to ON
#     reset_scan_type_sql_string = ""
#     for scan_type in scan_types:
#         reset_scan_type_sql_string = (
#             reset_scan_type_sql_string + f"SET {scan_type} = ON;"
#         )
#     query(reset_scan_type_sql_string)

#     # get the cost of scanning various relations
#     scan_types_qep_relations_costs = []
#     for i, scan_types_qep in enumerate(scan_types_qeps):

#         queried_relations = []

#         def recurse(qep):
#             if type(qep) is not dict:
#                 return
#             if "Relation Name" in qep.keys():
#                 queried_relations.append(qep)
#             if "Plan" in qep.keys():
#                 recurse(qep["Plan"])
#             if "Plans" in qep.keys():
#                 for plan in qep["Plans"]:
#                     recurse(plan)

#         recurse(scan_types_qep)

#         scan_types_qep_relations_costs.append({scan_types[i]: queried_relations})

#     # just get the information that we are interested in
#     for scan_types_qep_relations_cost in scan_types_qep_relations_costs:
#         print(scan_types_qep_relations_cost.keys(), "\n", file=stderr)

#         for key in scan_types_qep_relations_cost.keys():
#             for item in scan_types_qep_relations_cost[key]:
#                 for item_key in list(item):
#                     if item_key not in [
#                         "Node Type",
#                         "Relation Name",
#                         "Startup Cost",
#                         "Total Cost",
#                     ]:
#                         del item[item_key]
#                     if item_key == "Node Type":
#                         if item[item_key] == "Bitmap Heap Scan":
#                             item[item_key] = "Bitmap Scan"

#     print(scan_types_qep_relations_costs, file=stderr)
#     for scan_type in scan_types_qep_relations_costs:
#         print(scan_type.keys(), file=stderr)

#         for relation in scan_type.values():
#             print(relation, "\n", file=stderr)
#         print("\n\n", file=stderr)
#     return scan_types_qep_relations_costs


# """ #################################################################### 
# used to create the reset_sql_string to enable all types of joins and scans (to conduct a normal query)
# #################################################################### """


# def reset_connection_settings_string(reset_type):
#     reset_sql_string = ""

#     scan_types = [
#         "enable_bitmapscan",
#         "enable_indexscan",
#         "enable_seqscan",
#         "enable_tidscan",
#     ]
#     join_types = ["enable_hashjoin", "enable_mergejoin", "enable_nestloop"]

#     if reset_type == "all":
#         for scan_type in scan_types:
#             reset_sql_string = reset_sql_string + f"SET {scan_type} = ON;"
#         for join_type in join_types:
#             reset_sql_string = reset_sql_string + f"SET {join_type} = ON;"
#     if reset_type == "join":
#         for join_type in join_types:
#             reset_sql_string = reset_sql_string + f"SET {join_type} = ON;"
#     if reset_type == "scan":
#         for scan_type in scan_types:
#             reset_sql_string = reset_sql_string + f"SET {scan_type} = ON;"

#     return reset_sql_string
