''' SQL Statements '''

FROM = "FROM"
SELECT = "SELECT"
GROUP_BY = "GROUP BY"
ORDER_BY = "ORDER BY"

''' pgAdmin Table Prefix '''
var_prefix_to_table = {
    "r": "region",
    "n": "nation",
    "s": "supplier",
    "c": "customer",
    "p": "part",
    "ps": "partsupp",
    "o": "orders",
    "l": "lineitem",
}

''' PSQL '''
equality_comparators = {"!=", "="}
range_comparators = {"<=", ">=", ">", "<"}
operators = {"<", "=", ">", "!"}