# Project Analysis - Full Stack Web Developer Nanodegree Program

#### DESCRIPTION 
-  My assignment was to create a reporting tool that prints out reports (in plain text) based on the data in the database. This reporting tool is a Python program using the `psycopg2` module to connect to the database.

#### QUESTIONS
- What are the most popular three articles of all time?
- Who are the most popular article authors of all time?
- On which days did more than 1% of requests lead to errors?

#### EXECUTING THE PROGRAM
- To get started, you will need to download [Vagrant](https://www.vagrantup.com/downloads.html) and [Virtual Box](https://www.virtualbox.org/wiki/Downloads).
- Download database `news`: [here](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip)
- Use `vagrant up` to bring the virtual machine online and `vagrant ssh`to login.
- Place this file `newsdata.sql` on Vagrant folder: `/home/vagrant`
- Load up the database using `psql -d news -f newsdata.sql`
- Connect to the database using `psql -d news`
- Once you are located on database `news`, go ahead and input a `select * FROM authors;`to test out connection.
- Run the tool like this: `python3 python_log.py`

#### SQL Queries to answer the three questions:

`SELECT articles.title AS articles,count(log.path) AS
Number_Views FROM articles,log WHERE log.path
LIKE '%' || articles.slug AND log.status = '200 OK'
GROUP BY 1 ORDER BY 2 DESC LIMIT 3;`

`SELECT authors.name,count(log.id) FROM articles,authors,log 
WHERE articles.author = authors.id AND log.status = '200 OK' 
AND log.path LIKE '%' || articles.slug GROUP BY 1 
ORDER BY 2 DESC;`

`WITH r AS (SELECT DATE(log.time) AS date,COUNT(*) as num FROM
log WHERE log.status!='200 OK' GROUP BY date ORDER by date),
t AS (SELECT DATE(log.time) AS date,COUNT(*) AS count
FROM log GROUP BY date)SELECT r.date ,ROUND(100.0*r.num/t.count,2)
AS Percent FROM r,t WHERE r.date = t.date AND r.num > t.count/100;`

#### AUTHOR

- Leonardo Quitto - Buenos Aires , Argentina
