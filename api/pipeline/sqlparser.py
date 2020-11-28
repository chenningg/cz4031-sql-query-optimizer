from constant.constants import FROM, SELECT, GROUP_BY, ORDER_BY

class SQLParser: 

    def __init__(self): 
        self.comparison = collections.defaultdict(list)
        self.parenthesis = []
        self.select_attributes = []
        self.tables = []
        self.orderby_attributes = []
        self.groupby_attributes= []

    def clean_query(self, sql):
        return sql.replace("\t", "").replace("\n", " ")

    def parse_query(self, sql): 
        cleaned_sql = self.clean_query(sql)
        parsed = sqlparse.parse(cleaned_sql)
        stmt = parsed[0]
        from_seen, select_seen, where_seen, groupby_seen, orderby_seen = False, False, False , False, False

        for token in stmt.tokens:
            if select_seen:
                if isinstance(token, sqlparse.sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        self.select_attributes.append(identifier)
                elif isinstance(token, sqlparse.sql.Identifier):
                    self.select_attributes.append(token)
            if from_seen:
                if isinstance(token, sqlparse.sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        self.tables.append(identifier)
                elif isinstance(token, sqlparse.sql.Identifier):
                    self.tables.append(token)
            if orderby_seen:
                if isinstance(token, sqlparse.sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        self.orderby_attributes.append(identifier)
                elif isinstance(token, sqlparse.sql.Identifier):
                    self.orderby_attributes.append(identifier)
            if groupby_seen:
                if isinstance(token, sqlparse.sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        self.groupby_attributes.append(identifier)
                elif isinstance(token, sqlparse.sql.Identifier):
                    self.groupby_attributes.append(token)

            if isinstance(token, sqlparse.sql.Where):
                select_seen = False
                from_seen = False
                where_seen = True
                groupby_seen = False
                orderby_seen = False
                for where_tokens in token:
                    if isinstance(where_tokens, sqlparse.sql.Comparison):  
                        comparison_string = "{}\n".format(where_tokens)
                        comparison_key, comparison_operator, comparison_value = comparison_string.strip().split(' ')
                        self.comparison[comparison_key].append((comparison_operator, comparison_value))
                    elif isinstance(where_tokens, sqlparse.sql.Parenthesis):
                        parenthesis_string = "{}\n".format(where_tokens)
                        self.parenthesis.append(parenthesis_string)

            if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == GROUP_BY:
                select_seen = False
                from_seen = False
                where_seen = False
                groupby_seen = True
                orderby_seen = False
            if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == ORDER_BY:
                select_seen = False
                from_seen = False
                where_seen = False
                groupby_seen = False
                orderby_seen = True
            if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == FROM:
                select_seen = False
                from_seen = True
                where_seen = False
                groupby_seen = False
                orderby_seen = False
            if token.ttype is sqlparse.tokens.DML and token.value.upper() == SELECT:
                select_seen = True
                from_seen = False
                where_seen = False
                groupby_seen = False
                orderby_seen = False