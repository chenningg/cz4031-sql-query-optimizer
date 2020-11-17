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
10. Download [Picasso](https://dsl.cds.iisc.ac.in/projects/PICASSO/picasso_download/license.htm). Make sure to select the full library (we recommend getting the zip file). Extract it.
11. Ensure you have at least JDK 6.0 installed. We suggest the latest version of [AdoptOpenJDK](https://adoptopenjdk.net/releases.html). If you have your Java environment set up, navigate to `./PicassoRun/Windows/` and run `activatedb.bat`, `compileServer.bat` and `compileClient.bat` in this order to compile the Java files.
12. To connect to the Postgresql database, we will need to update our JDBC driver to the latest version. The JDBC driver serves to connect the Java application to our Postgresql database. Download it [here](https://jdbc.postgresql.org/download.html#current).
13. Navigate to `./Libraries/` and find the jar file for the old JDBC driver for Postgresql. It should be named something like `postgresql-8.0-311.jdbc3`. Replace this file with the latest version that you just downloaded. Rename it so it matches the old name (e.g. `postgresql-8.0-311.jdbc3`) exactly, so that Picasso can detect it.
14. Navigate back to `./PicassoRun/Windows/`. We can now start the program. Run `runServer.bat` to start the Picasso server, then run `runClient.bat` to run the Picasso client. A GUI should pop up. Click on `Enter`, and enter the connection details (`localhost` and port `4444` by default).
