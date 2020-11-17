<h1 align="center">SQL Query Optimizer</h1>

An SQL query optimizer that executes an SQL query plan and visualizes its performance, made for a project for NTU's CZ4031 (Database System Principles) course.

![Tables present in the database](https://i.imgur.com/MrvHfD9.png)

Queries are tested against [TPC-H](http://www.tpc.org/tpch/), a benchmark for generating dummy data in a database that attempts to mimic real world operations. The tables present in the database are shown in the image above.

## Installation and setup

1. Ensure that you have [Postgresql](https://www.postgresql.org/download/) installed. This project may work on other databases, but has only been tested on Postgresql.
2. Run [pgAdmin](https://www.pgadmin.org/), which should come bundled in the Postgresql installation. If it's your first time accessing it, it will prompt you to create a root user and password - name this user `postgres` and supply your own password. Create a new database named "TPC-H".
3. Clone this repository into a new folder.
4. Open your terminal and run `psql -U postgres -f dss.ddl TPC-H` from the cloned repository's folder. This command connects you to Postgresql as the default user `postgres`, and runs the SQL commands found in dss.ddl on the database `TPC-H`. The commands will initialize empty tables in the database similar to the ones shown in the image at the top.
5. After the tables are created, run `psql -U postgres -f dss.ri TPC-H`. This command will create the constraints on the tables, including initializing the primary keys and foreign keys on the various tables.
6. You may generate your own dummy data using [TPC-H](http://www.tpc.org/tpch/), or use our pre-generated data, found in this [Google drive](https://drive.google.com/drive/folders/1i7FYWI1ePuFFZpMdRO7gwVD2lLw_j03B?usp=sharing). Download `data.zip` and extract it. Each csv file corresponds and contains data of a table in the database.
7. Navigate back to the pgAdmin interface. Right click each table and click on `Import/Export`. Import the corresponding csv file into each table, with the format set to `csv` and encoding set to `UTF-8`. Set the delimeter to `|` and click OK to import the data.
8. Once all data has been imported, right click each table and verify the data by clicking `View/Edit Data` > `First 100 Rows`.
9. If all the data seems correct, right click each table and click on `Maintenance`. Tick `Vaccuum`, and turn `Analyze` and `Verbose Messages` on. Run this for each table.
