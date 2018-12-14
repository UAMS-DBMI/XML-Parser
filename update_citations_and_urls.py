#!/usr/bin/env python3

import argparse
from bs4 import BeautifulSoup
from ftfy import fix_text
from time import sleep
import csv
import scholar

def main(publications_file, titleinfo_file, cookiejar, delay=10):
    # Set up the querier
    querier = scholar.ScholarQuerier()
    querier.apply_settings(scholar.ScholarSettings())
    query = scholar.SearchScholarQuery()
    scholar.ScholarConf.COOKIE_JAR_FILE = cookiejar

    with open(publications_file, "r", encoding="utf8") as f:
        xml = f.read()

    soup = BeautifulSoup(xml, "lxml")

    # Get the titles of all publications from the EndNote file
    record_titles = []
    for record in soup.xml.records:
        record_titles.append(fix_text(record.titles.title.text))

    # Get any titles that are already in titleinfo.csv, if it exists. If not, then
    # create the file.
    file_titles = []
    try:
        with open(titleinfo_file, "r", encoding="utf8") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    file_titles.append(fix_text(row[0]))
                except IndexError:
                    pass
    except FileNotFoundError:
        with open(titleinfo_file, "w", encoding="utf8") as f:
            pass

    # If the info isn't already in the file, then query Google Scholar for the URL
    # and citation count, and write it into the file.
    with open(titleinfo_file, "a", newline="", encoding="utf8") as f:
        writer = csv.writer(f)

        for record_title in record_titles:
            if record_title not in file_titles:
                query.set_phrase(record_title)
                query.set_num_page_results(1)

                querier.send_query(query)

                try:
                    url = querier.articles[0]["url"]
                except IndexError:
                    url = ""
                if url != None:
                    if "scholar.google.com" in url:
                        url = url[26:]
                try:
                    citations = querier.articles[0]["num_citations"]
                except IndexError:
                    citations = ""

                if citations == None:
                    citations = 0
                if url == None:
                    url = ""

                print(record_title)
                print(citations)
                print(url + "\n")

                writer.writerow(
                    [fix_text(record_title), fix_text(str(citations)), fix_text(url)]
                )

                sleep(request_delay)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Create or update the titleinfo cache with the citation "
        "count and URL of each publication."
    )

    parser.add_argument(
        "publications_file",
        help="An XML file exported from EndNote, with a list of publications"
    )
    parser.add_argument(
        "titleinfo_file",
        help="The CSV file to write output to. It will contain title, "
        "citation count and URL for each publication"
    )

    parser.add_argument(
        "--cookie_jar",
        help="File to cache cookies to; default is scholar-cookies.txt",
        default="scholar-cookies.txt"
    )

    parser.add_argument(
        "--request_delay",
        type=int,
        help="Number of seconds to wait between each request to Google Scholar; "
        "default is 10. WARNING: If you reduce this, you WILL get banned from "
        "Google Scholar!",
        default=10
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(
        args.publications_file,
        args.titleinfo_file,

        args.cookie_jar,
        args.request_delay
    )
