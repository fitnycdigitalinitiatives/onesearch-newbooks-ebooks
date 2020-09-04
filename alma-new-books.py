#!/usr/bin/env python

import urllib.parse
import urllib.request
import os
import xmltodict
import pprint
import json

base_url = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports"
api_key = os.environ["API_KEY"]
gb_api_key = os.environ["GB_EBOOKS_API_KEY"]
path = (
    "/shared/Fashion Institute of Technology 01SUNY_FIT/Reports/20200331-new-ebook-list"
)
params = {"apikey": api_key, "path": path, "limit": "200", "col_names": "true"}
url = base_url + "?" + urllib.parse.urlencode(params)

# function to lookup Google Books API by ISBN
def isbn_lookup(ISBNs):
    ISBNlist = ISBNs.split("; ")
    for ISBN in ISBNlist[:1]:
        gb_url = (
            "https://www.googleapis.com/books/v1/volumes?key="
            + gb_api_key
            + "&q=isbn:"
            + ISBN
            + "&fields=totalItems,items/id,items/volumeInfo(title,description,previewLink,imageLinks)&maxResults=1"
        )
        with urllib.request.urlopen(gb_url) as gb_response:
            gb_api = gb_response.read()
            gb_json_data = json.loads(gb_api)
            if "items" in gb_json_data:
                try:
                    thumbnail = gb_json_data["items"][0]["volumeInfo"]["imageLinks"][
                        "thumbnail"
                    ]
                    return thumbnail.replace("http:", "https:")
                except Exception as e:
                    thumbnail = ""
    return ""


with urllib.request.urlopen(url) as response:
    xml = response.read()
    dict = xmltodict.parse(xml)
    records = dict["report"]["QueryResult"]["ResultXml"]["rowset"]["Row"]
    formatted_records = []
    for record in records:
        formatted_record = {
            "title": "",
            "author": "",
            "onesearch-url": "",
            "cover-url": "",
        }
        if "Column4" in record:
            formatted_record["title"] = record["Column4"].replace("/", "").rstrip()
        if "Column1" in record:
            formatted_record["author"] = record["Column1"]
        if "Column3" in record:
            formatted_record["onesearch-url"] = (
                "https://onesearch.fitnyc.edu/discovery/fulldisplay?docid=alma"
                + record["Column3"]
                + "&context=L&vid=01SUNY_FIT:01SUNY_FIT&search_scope=MyInst_and_CI&tab=Everything&lang=en"
            )
        if "Column2" in record:
            ISBNs = record["Column2"]
            formatted_record["cover-url"] = isbn_lookup(ISBNs)

        if formatted_record["cover-url"] != "":
            formatted_records.append(formatted_record)

    filename = "gh-pages/new-books.json"
    with open(filename, "w") as outfile:
        json.dump(formatted_records, outfile, indent=4)
