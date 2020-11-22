<h1 align="center">Frontend</h1>

This package houses the frontend for our query optimizer. It takes in a user supplied SQL query made for the [TPC-H](http://www.tpc.org/tpch/) dataset and turns it into a query template that is parsed by [Picasso](https://dsl.cds.iisc.ac.in/projects/PICASSO/). It then generates an explanation on how the query optimizer determines the optimal query execution plan to pick from various plans by running it through a commercial database management system's query optimizer (defaults to Postgresql).

## Installation and setup

1. Ensure that you have [Yarn](https://yarnpkg.com/getting-started) (A package manager for javascript) installed.
2. `cd` into this folder and run `yarn install` to install the dependencies needed for the client.
3. In your terminal, run `yarn start` to start both the frontend client and the backend API server concurrently. Make sure to check out the `api` folder if you haven't set up the API server yet.
