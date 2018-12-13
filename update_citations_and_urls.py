#!/usr/bin/env python3

from bs4 import BeautifulSoup
from ftfy import fix_text
from time import sleep
import csv
import scholar

#Set up the querier
querier = scholar.ScholarQuerier()
querier.apply_settings(scholar.ScholarSettings())
query = scholar.SearchScholarQuery()
scholar.ScholarConf.COOKIE_JAR_FILE = "scholar-cookies.txt"

with open("Pubs_basedon_TCIA0618.xml","r",encoding="utf8") as f:
    xml = f.read()

soup = BeautifulSoup(xml,"lxml")

#Get the titles of all publications from the EndNote file
record_titles = []
for record in soup.xml.records:
    record_titles.append(fix_text(record.titles.title.text))

#Get any titles that are already in titleinfo.csv, if it exists. If not, then
#create the file.
file_titles = []
try:
    with open("titleinfo.csv","r",encoding="utf8") as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                file_titles.append(fix_text(row[0]))
            except IndexError:
                pass
except FileNotFoundError:
    with open("titleinfo.csv","w",encoding="utf8") as f:
        pass

#If the info isn't already in the file, then query Google Scholar for the URL
#and citation count, and write it into the file.
with open("titleinfo.csv","a",newline="",encoding="utf8") as f:
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
            
            writer.writerow([fix_text(record_title),fix_text(str(citations)),
                             fix_text(url)])
            
            sleep(10)
