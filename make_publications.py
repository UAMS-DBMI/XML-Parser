#!/usr/bin/env python3

from bs4 import BeautifulSoup
from collections import Counter
from re import sub
import ftfy
import csv
import argparse
import os


class Record:
    def __init__(
        self,
        i="",
        authors="",
        title="",
        periodical="",
        year="",
        pubtype="",
        citations="",
        url="",
        abstract="",
        keywords="",
        abstract_div="",
    ):
        self.i = i
        self.authors = authors
        self.title = title
        self.periodical = periodical
        self.year = year.strip()
        self.pubtype = pubtype
        self.citations = citations
        self.url = url
        self.abstract = abstract
        self.keywords = keywords
        if self.keywords == []:
            self.keywords = ""
        self.abstract_div = abstract_div

    def __str__(self):
        return """
        <div id="{0}" class="paper droppable">
            <h4>{1}</h4>
            <author>{2}</author>
            <br><periodical>{3}</periodical> <year>{4}</year>
            <pub-type> - {5}</pub-type>{6}
            <br>{7}
            {8}
            {9}
            {10}
        </div>
     """.format(
            *self.tuple_form()
        )

    def tuple_form(self):
        return (
            self.i,
            self.title,
            self.authors,
            self.periodical,
            self.year,
            self.pubtype,
            self.citations,
            self.url,
            self.abstract,
            self.keywords,
            self.abstract_div,
        )

paperpile_html = """<!DOCTYPE html>
<html>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="https://wiki.cancerimagingarchive.net/s/en_GB/7400/f2dd15fadfb45568d4c57973599993b8f86142a0/28/_/favicon.ico">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/js-cookie@2/src/js.cookie.min.js"></script>

    <!--

    Created by Ayanle Hashi (2018)
    George Mason University
    Email: ahashi2000@gmail.com
    Repository: https://github.com/AyanleHashi/XML-Parser

    -->

    <head>
        <title>TCIA Publications</title>
        <style>
            html {{
                font-family: "Arial";
                overflow-y: scroll;
            }}
            periodical {{
                color: green;
                font-style: italic;
            }}
            pub-type {{
                color: #666666;
            }}
            h4 {{
                margin-bottom: 0px;
                color: #009;
            }}
            a {{
                text-decoration: none;
            }}
            img {{
                max-width: 100%;
                max-height: 100%;
            }}
            #wrapper {{
                position: fixed;
                top: 0;
                width: 22vw;
                height: 100%;
                background-color: #eee;
                z-index: 5;
                right: 0vw;
            }}
            #sidebar {{
                position: relative;
                top: 100px;
                left: 1vw;
                height: 91vh;
                overflow-y: scroll;
                width: 22vw;
            }}
            #header {{
                position: fixed;
                height: 100px;
                width: 100%;
                z-index: 4;
                background-color: #eee;
                border-bottom: 2px solid #ccc;
                float: left;
            }}
            #labelInput {{
                width: 70%;
            }}
            #imagediv {{
                position: fixed;
                width: 24vw;
                top: 100px;
            }}
            .paper {{
                padding-bottom: 20px;
            }}
            .input-group {{
                width: 45vw;
                padding-top: 30px;
                left: 17vw;
            }}
            .container {{
                padding-top: 110px;
                margin-left: 2vw;
                width: 75vw;
                border: 0px solid #ccc;
            }}
            .draggable {{
                height: 40px;
                display: inline-block;
                background: #ddd;
                border-radius: 5px;
                border: 1px solid #666;
                padding: 10px;
            }}
            .draggable-after {{
                height: 40px;
                display: inline-block;
                background: #ddd;
                border-radius: 5px;
                border: 1px solid #666;
                padding: 10px;
            }}
            .btn:focus {{
                outline: none;
            }}
            .btn-link {{
                padding: 0px;
            }}
            .abstract {{
                border-top: 1px solid #ddd;
            }}
            .selected {{
                font-weight: Bold;
            }}
            .pagination {{
                margin-left: 4vw;
                margin-right: 20vw;
            }}
            .padding-0 {{
                padding-left: 0px;
                padding-right: 0px;
            }}
            .btn {{
                text-align: lef !important;
                white-space: normal !important;
            }}
        </style>

        <script>
        //Split the document into e pages and reset the page number to 1
        function paginate(e) {{
        	$(".paper").each(function(index,element) {{
		        $(this).attr("id",index+1);
	        }});

            $(".container").find(".paper").hide();
            for (var i=1;i<e+1;i++) {{
                $("#" + String(i)).show();
            }}

            window.location.href = "#";
            $("li").removeClass("active");
            $("a[href=\\"#1\\"]").parent().addClass("active");
            window.scrollTo(0,0);
        }}

        $(document).ready(function() {{
            var COOKIES = {{}};
            var elements_per_page = 25;
            $('[data-toggle="tooltip"]').tooltip();

            //Add the first page to the site
            $(".pagination").html("");
            for (var i=1;i<($(".paper").length / elements_per_page)+1;i++) {{
                $(".pagination").append("<li><a href=\\"#" + String(i) + "\\">" + String(i) + "</a></li>");
            }}

            paginate(elements_per_page);

            //Set the cookies if they don't already exist

            //Temporarily hide any papers that don't contain the text entered in the search bar
            $("#searchbar").on("keyup", function() {{
                $(".container").find("li").removeClass("active");
                $(".sidebar-tag").removeClass("selected");
                $(".pagination").hide();
                var value = $(this).val().toLowerCase();

                if (value.indexOf("author:") > -1) {{
                    $(".container .paper").filter(function() {{
                        $(this).toggle($(this).find("author").text().toLowerCase().indexOf(value.substring(7,value.length).replace(/^\\s/,"")) > -1);
                    }});
                }}
                else if (value.indexOf("year:") > -1) {{
                    $(".container .paper").filter(function() {{
                        $(this).toggle($(this).find("year").text().toLowerCase().indexOf(value.substring(5,value.length).replace(/^\\s/,"")) > -1);
                    }});
                }}
                else if (value.indexOf("title:") > -1) {{
                    $(".container .paper").filter(function() {{
                        $(this).toggle($(this).find("h4").text().toLowerCase().indexOf(value.substring(6,value.length).replace(/^\\s/,"")) > -1);
                    }});
                }}
                else if (value == "") {{
                    paginate(elements_per_page);
                    $("#searchbar").focus();
                    $(".pagination").show();
                }}
                else {{
                    $(".container .paper").filter(function() {{
                        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
                        //$(this).toggle($(this).find("h4").text().toLowerCase().indexOf(value) > -1);
                    }});
                }}
            }});

            //On clicking a new page number, update the pagination and switch pages
            $(".pagination").children().each(function(index) {{
                var that = this;
                $(that).on("click","a",function() {{
                    $(that).parent().find("li").removeClass("active");
                    $(that).addClass("active");
                    $("a[href=\\"#"+$(that).text()+"\\"]").addClass("active");
                    $(".container").find(".paper").hide();
                    $(".paper").each(function(index2) {{
                        if ((parseInt($(that).text()) - 1) * elements_per_page < parseInt($(this).attr("id")) && parseInt($(this).attr("id")) <= parseInt($(that).text()) * elements_per_page) {{
                            $(this).show();
                        }}
                    }});
                    window.scrollTo(0,0);
                }});
            }});

            //Filter papers by the sidebar tag
            $(".sidebar-tag").on("click",function() {{
                $(".pagination").hide();
                var value = $(this).text();
                $(".sidebar-tag").removeClass("selected");
                $(this).addClass("selected");
                $(".paper").filter(function() {{
                    $(this).toggle($(this).find(".tag").text().indexOf("· " + value + " ·") > -1);
                }});
            }});

            //Display all papers after a filter
            $("#clear").on("click",function() {{
                $(".pagination").show();
            }});

            //Sort by whichever option is selected
            $("#sel1").change(function() {{
                var sortby = $(this).find(":selected").text();
                var tag = "";
                $(".paper").show();

                if (sortby === "First Author") {{
                    tag = "author";
                }}
                else if (sortby === "Publication Date") {{
                    tag = "year";
                }}
                else if (sortby === "Title") {{
                    tag = "h4"
                }}
                var OrderedDivs = $(".paper").sort(function (a, b) {{
                    if (tag == "year") {{
                        return ($(a).find(tag).text().toLowerCase().replace("“","") < $(b).find(tag).text().toLowerCase()) ? 1 : -1;
                    }}
                    else {{
                        return ($(a).find(tag).text().toLowerCase().replace("“","") > $(b).find(tag).text().toLowerCase()) ? 1 : -1;
                    }}
                }});

                $(".container").html(OrderedDivs);

                paginate(elements_per_page);
	        }});
        }});
        </script>
    </head>

    <body>
        <div id="header">
            <div class="row">
                <div class="input-group">
                    <div class="col-xs-6 padding-0">
                        <input id="searchbar" type="text" class="form-control searchbar" name="Searchbar" autofocus>
                    </div>

                    <div class="col-xs-3 padding-0">
                        <select class="form-control" id="sel1">
                            <option>Sort by:</option>
            			    <option>First Author</option>
                			<option>Publication Date</option>
                			<option>Title</option>
                		</select>
                	</div>

                	<div class="col-xs-1 padding-0">
                	    <span class="glyphicon glyphicon-question-sign" style="font-size:32px;padding-left:8px;color:#1F77B4;" data-toggle="tooltip" data-placement="bottom" data-original-title="" title="Search using &quot;author:&quot;, &quot;title:&quot;, or &quot;year:&quot;"></span>
                	</div>
                	<div class="col-xs-1 padding-0">
                	    <a href="endnote/{endnote}" download><span class="glyphicon glyphicon-download-alt" style="font-size:32px;" data-toggle="tooltip" data-placement="bottom" data-original-title="" title="Download EndNote file"></span></a>
                	</div>
                	<div class="col-xs-1 padding-0">
                        <button type="button" class="btn btn-link" data-toggle="modal" data-target="#myModal"><span class="glyphicon glyphicon-stats" style="font-size:32px;" data-backdrop="false" data-toggle="tooltip" data-placement="bottom" data-original-title="" title="View publication statistics"></button>
                	</div>
            	</div>
            </div>

        </div>

        <div id="wrapper">
            <div id="sidebar">
                <form action="" method="POST">
                    <!--<input id="labelInput" type="text" class="form-control searchbar" name="label" placeholder="Add label">
                    <button id="labelSubmit" class="btn">Add</button><br><br>-->
                    <b>Keywords</b>
                    <form action="">
                        <button type="submit" class="btn btn-link" id="clear"><b>(Clear)</b></button><br>
                    </form>
                    {}
                </form>
            </div>
        </div>

        <div id="myModal" class="modal fade" role="dialog">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal"><i class="icon-remove"></i></button>
                        <h4 class="modal-title">Publications Over Time</h4>
                    </div>
                    <div class="modal-body">
                        <img src="TCIAGraph.svg">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="container">
            {}
        </div>
        <ul class="pagination pagination-sm"></ul>
    </body>
</html>
"""

def main(titleinfo_file, publications_file, output_file):

    with open(titleinfo_file, "r", encoding="utf8") as f:
        reader = csv.reader(f)
        title_info = []
        for row in reader:
            title_info.append((row[0], row[1], row[2]))

    with open(publications_file, encoding="utf8") as f:
        xml = f.read()

    records = []
    soup = BeautifulSoup(xml, "lxml")

    abstract_number = 1
    keyword_number = 1
    record_number = 1
    ALL_KEYWORDS = []

    for record in soup.xml.records:
        authors = ""
        try:
            for author in record.contributors.authors:
                authors += author.text + "; "
        except AttributeError:
            continue

        authors = ftfy.fix_text(authors[:-2])
        title = record.titles.title.text
        try:
            periodical = record.periodical.find_all("full-title")[0].text + ", "
        except AttributeError:
            periodical = ""
        year = record.dates.year.text
        pubtype = record.find_all("ref-type")[0]["name"]

        citations = ""
        info_url = ""
        for i in title_info:
            if title.replace("‐", "-") == i[0].replace("‐", "-"):
                citations = ", cited " + i[1] + " times"
                if i[1] == "1":
                    citations = citations[:-1]
                if len(i[2]) == 0:
                    info_url = ""
                else:
                    info_url = (
                        '<a href="'
                        + str(i[2])
                        + '"><span class="glyphicon glyphicon-link"></span>Website</a>'
                    )
        if len(citations) == 0:
            citations = ", cited 0 times"

        try:
            url = (
                '<a href="'
                + record.urls.find_all("related-urls")[0].url.text
                + '"><span class="glyphicon glyphicon-link"></span>Website</a>'
            )
        except IndexError:
            url = info_url
        try:
            abstract = """<button type="button" class="btn btn-link" data-toggle="collapse" data-target="#abstract{0}"><span class="glyphicon glyphicon-arrow-down"></span>Abstract</button>""".format(
                abstract_number
            )
            abstract_div = """<div id="abstract{0}" class="collapse abstract">{1}</div>""".format(
                abstract_number, record.abstract.text
            )
            abstract_number += 1
        except AttributeError:
            abstract = ""
            abstract_div = ""

        keyword_list = []
        keyword_list_div = ""
        try:
            for kw in record.keywords:
                s = ftfy.fix_text(kw.text.lower())
                if "," in s:
                    keyword_list.extend([x.strip() for x in s.split(", ")])
                    ALL_KEYWORDS.extend([x.strip() for x in s.split(", ")])
                else:
                    keyword_list.append(s)
                    ALL_KEYWORDS.append(s)
            keyword_list = "· " + " · ".join(keyword_list) + " ·"
            keyword_list = """<button type="button" class="btn btn-link" data-toggle="collapse" data-target="#tag{0}"><span class="glyphicon glyphicon-tag"></span>Keywords</button>
                <div id="tag{0}" class="collapse tag"> {1} </div>""".format(
                keyword_number, keyword_list
            )

            keyword_number += 1
        except:
            pass

        records.append(
            Record(
                str(record_number),
                authors,
                title,
                periodical,
                year,
                pubtype,
                citations,
                url,
                abstract,
                keyword_list,
                abstract_div,
            )
        )
        record_number += 1

    entry = ""
    for r in records:
        entry += str(r)

    ALL_KEYWORDS = sorted([sub('["\\t]', "", x.lower()) for x in ALL_KEYWORDS])
    counter = Counter(ALL_KEYWORDS)
    keywords_to_add = ""
    for c in counter.keys():
        if counter[c] > 1:
            keywords_to_add += (
                '<button type="button" class="btn btn-link sidebar-tag">'
                + c
                + "</button> ("
                + str(counter[c])
                + ")<br>\n"
            )


    with open(output_file, "w", encoding="utf8") as f:
        f.write(paperpile_html.format(keywords_to_add, entry, 
                                      endnote=os.path.basename(publications_file)))


def parse_args():
    parser = argparse.ArgumentParser(
        description='Render a static HTML page from an EndNote file and '
        'a titleinfo file.'
    )

    parser.add_argument(
        "titleinfo",
        help="A csv file containing a title, citation count, and url for each "
        "publication; this is the file produced by update_citations_and_urls.py"
    )
    parser.add_argument(
        "endnote",
        help="An XML file exported from EndNote, with a list of publications"
    )
    parser.add_argument(
        "output",
        help="The filename to write output to"
    )

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    main(
        args.titleinfo,
        args.endnote,
        args.output
    )
