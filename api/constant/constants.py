''' SQL Statements '''

FROM = "FROM"
SELECT = "SELECT"
GROUP_BY = "GROUP BY"
ORDER_BY = "ORDER BY"

''' pgAdmin Table Prefix '''
var_prefix_to_table = {
    "r_": "region",
    "n_": "nation",
    "s_": "supplier",
    "c_": "customer",
    "p_": "part",
    "ps_": "partsupp",
    "o_": "orders",
    "l_": "lineitem",
}

''' PSQL '''
equality_comparators = ["!=", "="]
range_comparators = ["<=", ">=", ">", "<"]