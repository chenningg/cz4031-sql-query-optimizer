import sqlparse
import collections 
from constant.constants import (
    operators,
    range_comparators
)
from operator import mul, add, sub, truediv
from constant.constants import FROM, SELECT, GROUP_BY, ORDER_BY
from custom_errors import *


class SQLParser:
    def __init__(self):
        try:
            self.comparison = collections.defaultdict(list)
            self.parenthesis = []
            self.select_attributes = []
            self.tables = []
            self.orderby_attributes = []
            self.groupby_attributes = []
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError(
                "Error in sqlparser init - Unable to initialize the class."
            )

    def clean_query(self, sql):
        try:
            # date
            sql = sql.replace(" date ", " ")

            # +
            found = False
            start, end = 0, 0
            start = self.query_index("+ interval", sql)
            if start != -1:
                found = True
            if found:
                for i in range(start, len(sql) - 1):
                    if ord(sql[i]) == 10:
                        end = i
                        break
                sql = sql[:start] + sql[end:]

            # between and calculate
            while self.query_index("between", sql) != -1:
                between_start = self.query_index("between", sql)
                between_end = between_start + len("between")
                if sql[between_end + 1].isnumeric():  # between a number to number
                    i = between_end + 1
                    calc_end = 0
                    while sql[i] != "a" and sql[i] != "A":
                        calc_end = i - 1
                        i += 1
                    first_expression = sql[between_end + 1 : calc_end + 1]

                    while not sql[i].isnumeric():
                        second_calc_start = i
                        i += 1

                    while ord(sql[i]) != 10:
                        second_calc_end = i
                        i += 1

                    second_expression = sql[second_calc_start + 1 : second_calc_end + 1]
                    sql = (
                        sql[: between_end + 1]
                        + "{}".format(self.calculate(first_expression))
                        + sql[calc_end + 1 : second_calc_start + 1]
                        + "{}".format(self.calculate(second_expression))
                        + sql[second_calc_end + 1 :]
                    )

                start = 0
                for i in range(between_start - 2, -1, -1):
                    if ord(sql[i]) == 32:
                        start = i + 1
                        break
                predicate_to_add = sql[start : between_start - 1]
                rest = sql[between_end + 1 :]
                and_start = self.query_index("and", rest)
                sql = (
                    sql[:between_start]
                    + ">= "
                    + rest[: and_start + 3]
                    + " {} <=".format(predicate_to_add)
                    + rest[and_start + 3 :]
                )

            sql = sql.replace("\t", "").replace("\n", " ")
            return sql
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError("Error in clean_query() - Unable to clean the SQL query.")

    def parse_query(self, sql):
        try:
            nested_sql_ = self.nested_query(sql)
            nested_sql = self.remove_double_spacing(nested_sql_)
            formatted_sql = self.sql_formatter(nested_sql)
            cleaned_sql = self.clean_query(formatted_sql)
            parsed = sqlparse.parse(cleaned_sql)
            stmt = parsed[0]
            from_seen, select_seen, where_seen, groupby_seen, orderby_seen = (
                False,
                False,
                False,
                False,
                False,
            )

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
                            (
                                comparison_key,
                                comparison_operator,
                                comparison_value,
                            ) = comparison_string.strip().split(" ")
                            self.comparison[comparison_key].append(
                                (comparison_operator, comparison_value)
                            )
                        elif isinstance(where_tokens, sqlparse.sql.Parenthesis):
                            parenthesis_string = "{}\n".format(where_tokens)
                            self.parenthesis.append(parenthesis_string)

            if (
                token.ttype is sqlparse.tokens.Keyword
                and token.value.upper() == GROUP_BY
            ):
                select_seen = False
                from_seen = False
                where_seen = False
                groupby_seen = True
                orderby_seen = False
            if (
                token.ttype is sqlparse.tokens.Keyword
                and token.value.upper() == ORDER_BY
            ):
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
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError("Error in parse_query() - Unable to parse the SQL query.")

    def query_index(self, inside, whole):
        try:
            window = len(inside)
            n = len(whole)

            if window > n:
                return -1

            base = 26
            MOD = 10 ** 9 + 7

            charToInt = lambda ch: ord(ch) - ord("a")

            hash1, hash2 = 0, 0
            for i in range(window):
                hash1 = (hash1 * base + charToInt(whole[i])) % MOD
                hash2 = (hash2 * base + charToInt(inside[i])) % MOD

            if hash1 == hash2:
                return 0

            start = 1

            while start < n - window + 1:
                hash1 = (
                    hash1 * base
                    - charToInt(whole[start - 1]) * (base ** (window)) % MOD
                    + charToInt(whole[start + window - 1])
                ) % MOD
                if hash1 == hash2:
                    return start
                start += 1

            return -1
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError("Error in query_index() - Unable to query an index.")

    def calculate(self, s):
        try:
            OP = {"*": mul, "+": add, "-": sub, "/": truediv}
            op_set = {"+", "*", "-", "/"}
            cur_op = "+"
            cur_num, prev_num = "", ""
            for char in s:
                if char in op_set:
                    cur_op = char
                    prev_num = cur_num
                    cur_num = ""
                elif char != " ":
                    cur_num += char
            return OP[cur_op](float(prev_num), float(cur_num))
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError(
                "Error in calculate() - Unable to calculate attribute value."
            )

    def sql_formatter(self, sql):
        try:
          end = 0 
          temp = ""
          for index in range(1, len(sql)-1): 
              if sql[index] in operators: 
                  if sql[index-1] not in operators and ord(sql[index-1]) != 32: 
                      temp += sql[end: index] + ' ' 
                      end = index
                  if sql[index+1] not in operators and ord(sql[index+1]) != 32: 
                      temp += sql[end: index+1] + ' '
                      end = index + 1 

          temp += sql[end: len(sql)]
          return temp
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError(
                "Error in sql_formatter() - Unable to format the SQL statement."
            )

    def nested_query(self, sql): 
        try:
            select_index = []
            splitted_word_sql = sql.split(" ")
            
            for i, word in enumerate(splitted_word_sql): 
                if word == 'select\n' or word =='SELECT\n':
                    select_index.append(i)
            if len(select_index) == 2: 
                start_index = int(select_index[1])
                end_index = int(select_index[1])
                while not splitted_word_sql[start_index].startswith('('):
                    start_index -= 1  
                flag = False
                for i in range(start_index, start_index-3, -1): 
                    if splitted_word_sql[i] in range_comparators:
                        flag = True
                if flag:
                    start_part = splitted_word_sql[start_index][2:] if len(splitted_word_sql[start_index]) > 1 else splitted_word_sql[start_index]
                    while not splitted_word_sql[end_index].startswith(')'): 
                        end_index += 1
                    end_part = splitted_word_sql[end_index][1:] if len(splitted_word_sql[end_index]) > 1 else splitted_word_sql[end_index]
                    return " ".join(splitted_word_sql[:start_index] + [start_part]+ ['100'] + [end_part]+splitted_word_sql[end_index+1:])
            return sql
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError("Error in nested_query() - Unable to parse the nested query. Have mercy and give us something less nested please.")

    def remove_double_spacing(self, sql): 
        try:
            return sql.replace('  ', '')
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError("Error in remove_double_spacing() - Unable to remove double spacing.")
