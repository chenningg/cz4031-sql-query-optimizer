# SQL Query Optimizer (Frontend)

This package houses the frontend for our query optimizer. It takes in a user supplied SQL query made for the [TPC-H](http://www.tpc.org/tpch/) dataset and turns it into a query template that is parsed by [Picasso](https://dsl.cds.iisc.ac.in/projects/PICASSO/). It then generates an explanation on how the query optimizer determines the optimal query execution plan to pick from various plans by running it through a commercial database management system's query optimizer (defaults to Postgresql).
