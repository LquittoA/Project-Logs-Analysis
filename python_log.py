# !usr/bin/env python
# Logs Analysis Project by Leonardo Quitto

# PostgreSQL database adapter for the Python programming language
import psycopg2

# Built-in Database provided by Udacity to complete this project
DBNAME = "news"

_question1 = """SELECT articles.title AS articles,count(log.path) AS
                Number_Views FROM articles,log WHERE log.path
                LIKE '%' || articles.slug AND log.status = '200 OK' GROUP BY 1
                ORDER BY 2 DESC LIMIT 3;"""
_question2 = """SELECT authors.name,count(log.id) FROM articles,authors,log
                WHERE articles.author = authors.id AND log.status = '200 OK'
                AND log.path LIKE '%' || articles.slug GROUP BY 1
                ORDER BY 2 DESC;"""
_question3 = """WITH r AS (SELECT DATE(log.time) AS date,COUNT(*) as num FROM
                log WHERE log.status!='200 OK' GROUP BY date ORDER by date),
                t AS (SELECT DATE(log.time) AS date,COUNT(*) AS count
                FROM log GROUP BY date)SELECT r.date ,
                ROUND(100.0*r.num/t.count,2)
                AS Percent FROM r,t WHERE r.date = t.date
                AND r.num > t.count/100;"""


def connect_db(question):
    """This function connects to the database."""
    conn = psycopg2.connect(dbname=DBNAME)
    # Sending SQL statements and receiving results from the database
    c = conn.cursor()
    # Executing queries
    c.execute(question)
    # Fetching results
    records = c.fetchall()
    conn.close
    return records


def most_popular_three_articles(question):
    """This function anwers the first question"""
    results = connect_db(question)
    print("\nThe most popular three articles of all time are:\n")
    for i in results:
        print("\t" + str(i[0]) + "" + ": " + str(i[1]) + " views")
        print("")


def most_popular_article_authors(question):
    """This function anwers the second question"""
    results = connect_db(question)
    print("\nThe most popular article authors of all time:\n")
    for i in results:
        print("\t" + str(i[0]) + "" + ": " + str(i[1]) + " views")
        print("")


def requests_lead_errors(question):
    """This function anwers the third question"""
    results = connect_db(question)
    print("\nDays when more than 1% of requests lead to errors:\n")
    for i in results:
        print("\t" + str(i[0]) + "" + ": " + str(i[1]) + " errors")
        print("")


def main():
    """Main function"""
    most_popular_three_articles(_question1)
    most_popular_article_authors(_question2)
    requests_lead_errors(_question3)

main()