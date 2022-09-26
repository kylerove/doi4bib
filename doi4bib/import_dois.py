# -*- coding: UTF-8 -*-

"""
This file was copied from
https://github.com/OpenAPC/openapc-de/blob/master/python/import_dois.py

The only modifications I made were to remove some lines that were not
useful to me
"""

import json
from urllib.error import HTTPError
from urllib.parse import quote_plus, urlencode
from urllib.request import urlopen, Request

from Levenshtein import ratio

__all__ = ['crossref_query_title']

EMPTY_RESULT = {
    "crossref_title": "",
    "similarity": 0,
    "doi": ""
}
MAX_RETRIES_ON_ERROR = 3

PUBMED_EMPTY_RESULT = {
    "pubmed": ""
}
PUBMED_MAX_RETRIES_ON_ERROR = 1

def pubmed_query_title(title,journal,date):
    api_url = "https://pubmed.ncbi.nlm.nih.gov/api/citmatch/?"
    
    if journal is not None:
        params = {"method": "heuristic", "raw-text": title+". "+journal}
    elif date is not None:
        params = {"method": "heuristic", "raw-text": title+". "+date}
    else:
        params = {"method": "heuristic", "raw-text": title}
        
    url = api_url + urlencode(params, quote_via=quote_plus)
    request = Request(url)
    
    try:
        ret = urlopen(request)
        content = ret.read()
        data = json.loads(content.decode('utf-8'))
        success = data["success"]
        count = data["result"]["count"]
        
        if success is True and count == 1:
            top_hit = data["result"]["uids"][0]
            print(top_hit)
            return {"success": True, "result": top_hit}
        else:
            return {"success": False, "result": PUBMED_EMPTY_RESULT, "exception": "no match found"}
    except HTTPError as httpe:
        return {"success": False, "result": PUBMED_EMPTY_RESULT, "exception": httpe}

def crossref_query_title(title):
    """Contacts Crossref API for DOI of a paper

    The paper is identified by its title.
    The function retrieves the first 5 results, and searches for the one
    with maximum similarity to the original title.

    Raises an HTTPError in case of failure.

    Args:
        title: a str with the title of the paper whose DOI we are looking for
    """

    api_url = "https://api.crossref.org/works?"
    params = {"rows": "5", "query.title": title}
    url = api_url + urlencode(params, quote_via=quote_plus)
    request = Request(url)
    request.add_header("User-Agent",
                       "doi4bib utility\
                       (https://github.com/sharkovsky/doi4bib; mailto:kyle.rove@gmail.com)")
    try:
        ret = urlopen(request)
        content = ret.read()
        data = json.loads(content.decode('utf-8'))
        items = data["message"]["items"]
        most_similar = EMPTY_RESULT
        for item in items:
            title = item["title"].pop()
            result = {
                "crossref_title": title,
                "similarity": ratio(title.lower(),
                                    params["query.title"].lower()),
                "doi": item["DOI"]
            }
            if most_similar["similarity"] < result["similarity"]:
                most_similar = result
        return {"success": True, "result": most_similar}
    except HTTPError as httpe:
        return {"success": False, "result": EMPTY_RESULT, "exception": httpe}
