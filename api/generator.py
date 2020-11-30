import datetime
from datetime import date
from sys import stderr
from custom_errors import *


""" #################################################################### 
used to generate the combinations of queries for the selected predicates
#################################################################### """


class Generator:
    def generate_plans(
        self, arr, original_sql
    ):  # takes in array of selectivites per predicate, from get_selectivities
        try:
            res = []

            def helper(
                index, path, predicate_selectivities
            ):  # predicate_selectivities is like (predicate0 , 0.93) * (predicate1, 0.78) * 1.2...
                if index == len(arr):
                    res.append([path, predicate_selectivities])
                    return

                if len(arr[index]["conditions"]) == 1:  # only one comparator
                    for operator, v in arr[index]["conditions"].items():
                        queried_selectivity = v["queried_selectivity"]
                        for selectivity, val in v["histogram_bounds"].items():
                            # selectivity_as_percentage_of_base = float(selectivity / queried_selectivity)
                            old_val = v["histogram_bounds"][queried_selectivity]
                            selectivity_data = (
                                arr[index]["attribute"],
                                operator,
                                old_val,
                                val,
                                queried_selectivity,
                                selectivity,
                            )
                            helper(
                                index + 1,
                                self.find_and_replace(
                                    arr[index]["attribute"],
                                    operator,
                                    old_val,
                                    val,
                                    path,
                                ),
                                predicate_selectivities + [selectivity_data],
                            )

                elif len(arr[index]["conditions"]) == 2:  # range
                    count = 0
                    lessthan_histogram_bounds, morethan_histogram_bounds = [], []
                    operators = []
                    for operator, v in arr[index]["conditions"].items():
                        queried_selectivity = v["queried_selectivity"]
                        old_val = v["histogram_bounds"][queried_selectivity]
                        count += 1
                        if count == 1:  # < type
                            lessthan_histogram_bounds = [
                                (val, selectivity, queried_selectivity, old_val)
                                for selectivity, val in v["histogram_bounds"].items()
                            ]
                            operators.append(operator)
                        elif count == 2:  # > type
                            morethan_histogram_bounds = [
                                (val, selectivity, queried_selectivity, old_val)
                                for selectivity, val in v["histogram_bounds"].items()
                            ]
                            operators.append(operator)
                    for less_than, more_than in self.generate_ranges(
                        lessthan_histogram_bounds, morethan_histogram_bounds
                    ):  # ((val_less, sel_less, queried_sel), (val_more, sel_more, queried_sel))
                        more_than_path = self.find_and_replace(
                            arr[index]["attribute"],
                            operators[1],
                            more_than[3],
                            more_than[0],
                            path,
                        )
                        both_replaced_path = self.find_and_replace(
                            arr[index]["attribute"],
                            operators[0],
                            less_than[3],
                            less_than[0],
                            more_than_path,
                        )
                        selectivity_data = [
                            (
                                arr[index]["attribute"],
                                operators[0],
                                less_than[3],
                                less_than[0],
                                less_than[2],
                                less_than[1],
                            ),
                            (
                                arr[index]["attribute"],
                                operators[1],
                                more_than[3],
                                more_than[0],
                                more_than[2],
                                more_than[1],
                            ),
                        ]
                        helper(
                            index + 1,
                            both_replaced_path,
                            predicate_selectivities + selectivity_data,
                        )

            helper(0, original_sql, [])
            return res
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError(
                "Error in generate_plans() - Unable to generate plans for required selectivity variations."
            )

    def generate_ranges(
        self, lessthan_histogram_bounds, morethan_histogram_bounds
    ):  # for selectivities with more than 2 conditions (i.e. range)
        try:
            # less than should always have a greater value than the more than
            # all possible permutations
            res = [
                (x, y)
                for x in lessthan_histogram_bounds
                for y in morethan_histogram_bounds
                if x[0] > y[0]
            ]
            return res
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError(
                "Error in generate_ranges() - Unable to generate the required histogram bounds."
            )

    def find_and_replace(self, predicate, operator, old_val, new_val, sql_query):
        try:
            if isinstance(new_val, datetime.date):
                new_val = "'{}'".format(date.isoformat(new_val))
            if isinstance(old_val, datetime.date):
                old_val = "'{}'".format(date.isoformat(old_val))
            new_query = sql_query.replace(
                "{} {} {}".format(predicate, operator, old_val),
                "{} {} {}".format(predicate, operator, new_val),
            )
            return new_query
        except CustomError as e:
            raise CustomError(str(e))
        except:
            raise CustomError(
                "Error in find_and_replace() - Unable to replace the original attribute value with the new one."
            )
