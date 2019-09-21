# !usr/bin/env python
# Logs Analysis Project by Leonardo Quitto

# PostgreSQL database adapter for the Python programming language
import psycopg2
import sys

# Built-in Database provided by Udacity to complete this project
DBNAME = "news"

_question1 = """SELECT * FROM mostviews_articles limit 3;"""
_question2 = """SELECT * FROM article_authors;"""
_question3 = """SELECT error_logs.date,round(100.0*error_count/log_count,2) as percent
                FROM logs,error_logs WHERE logs.date = error_logs.date
                AND error_count > log_count/100;"""


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
    """This function anwers the first question"""
    results = connect_db(question)
    print("\nThe most popular article authors of all time:\n")
    for i in results:
        print("\t" + str(i[0]) + "" + ": " + str(i[1]) + " views")
        print("")


def requests_lead_errors(question):
    """This function anwers the first question"""
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