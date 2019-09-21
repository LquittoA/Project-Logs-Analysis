# Project Analysis - Full Stack Web Developer Nanodegree Program

#### DESCRIPTION 
-  My assignment was to create a reporting tool that prints out reports (in plain text) based on the data in the database. This reporting tool is a Python program using the `psycopg2` module to connect to the database.

#### QUESTIONS
- What are the most popular three articles of all time?
- Who are the most popular article authors of all time?
- On which days did more than 1% of requests lead to errors?

#### EXECUTING THE PROGRAM
- To get started, you will need to download [Vagrant](https://www.vagrantup.com/downloads.html) and [Virtual Box](https://www.virtualbox.org/wiki/Downloads).
- Use `vagrant up` to bring the virtual machine online and `vagrant ssh`to login.
- Download the data provided by Udacity. Unzip the file and place this file `newsdata.sql` on Vagrant folder `/home/vagrant`
- Load up the database using `psql -d news -f newsdata.sql`
- Connect to the database using `psql -d news`
- Once you are located on database `news`, go ahead and create the views you will see below.
- Run the tool like this: `python3 python_log.py`

#### Queries for creating views

 ```CREATE VIEW mostviews_articles AS SELECT articles.title,count(log.path) FROM articles,log WHERE log.path LIKE '%' || articles.slug AND log.status = '200 OK' GROUP BY articles.title ORDER BY 2 desc```
 
 ```CREATE VIEW logs AS SELECT to_char(time,'DD-MON-YYYY') AS Date, count(*) as Log_Count FROM log GROUP BY Date```
 
 ```CREATE VIEW article_authors AS SELECT title,name FROM articles,authors WHERE articles.author = authors.id```
 
 ```CREATE VIEW error_logs AS SELECT to_char(time,'DD-MON-YYYY') AS Date, count(*) AS error_count FROM log WHERE STATUS = '404 NOT FOUND' GROUP BY Date```
 
 