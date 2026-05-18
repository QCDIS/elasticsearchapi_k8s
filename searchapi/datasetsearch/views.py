# Basic Imports
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework import status

# Functional Imports
import json
import os
import re

import numpy as np
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from spellchecker import SpellChecker

# Create your views here.


# elasticsearch_url = os.environ['ELASTICSEARCH_URL']
# elasticsearch_username = os.environ.get('ELASTICSEARCH_USERNAME')
# elasticsearch_password = os.environ.get('ELASTICSEARCH_PASSWORD')
# base_path = os.environ.get('BASE_PATH').strip()
base_path = "search"

elasticsearch_host = os.environ.get('ELASTICSEARCH_HOST')
elasticsearch_username = os.environ.get('ELASTICSEARCH_USERNAME')
elasticsearch_password = os.environ.get('ELASTICSEARCH_PASSWORD')

es = Elasticsearch(
elasticsearch_host,
http_auth=(elasticsearch_username, elasticsearch_password),
verify_certs=False)
#ca_certs="/home/ubuntu/Development/test/indexer/web_indexers/http_ca.crt")


# Check if the connection is successful by pinging the ES instance
if es.ping():
    print("Connected to Elasticsearch")
else:
    print("Could not connect to Elasticsearch")
    #verify_certs=False
    print("Printing ping and information*****", es.ping())
    print(es.info())
    
aggregares = {
    "repo": {
        "terms": {
            "field": "repo.keyword",
            "size": 50,
        }
    },
    "spatial_coverage": {
        "terms": {
            "field": "spatial_coverage.keyword",
            "size": 50,
        }
    },
    "theme": {
        "terms": {
            "field": "theme.keyword",
            "size": 50,
        }
    },
    "publisher": {
        "terms": {
            "field": "publisher.keyword",
            "size": 50,
        }
    },
    "instrument": {
        "terms": {
            "field": "instrument.keyword",
            "size": 50,
        }
    },
}



# -----------------------------------------------------------------------------------------------------------------------
def getSearchResults(request, facet, filter, page, term):
    #es = Elasticsearch(elasticsearch_url, http_auth=[elasticsearch_username, elasticsearch_password])
    if filter != "" and facet != "":
        saved_list = request.session['filters']
        saved_list.append({"term": {facet + ".keyword": filter}})
        request.session['filters'] = saved_list
    else:
        if 'filters' in request.session:
            del request.session['filters']
        request.session['filters'] = []

    page = (int(page) - 1) * 10
    result = {}
    if term == "*" or term == "top10":
        result = es.search(
            index="dataset",
            body={
                "from": page,
                "size": 10,
                "query": {
                    "bool": {
                        "must": {
                            "match_all": {}
                        },
                        "filter": {
                            "bool": {
                                "must": request.session.get('filters')
                            }
                        }
                    }
                },
                "aggs": aggregares
            }
        )
    else:
        user_request = "some_param"
        query_body = {
            "from": page,
            "size": 10,
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": term,
                            "fields": ["description", "keywords", "contact", "publisher", "citation",
                                       "genre", "creator", "headline", "abstract", "theme", "producer", "author",
                                       "sponsor", "provider", "title",
                                       "instrument", "maintainer", "editor",
                                       "copyrightHolder", "contributor", "contentLocation", "about", "rights",
                                       "useConstraints",
                                       "status", "scope", "metadataProfile", "metadataIdentifier", "distributionInfo",
                                       "dataQualityInfo",
                                       "contentInfo",
                                       "repo",
                                       "essential_variables",
                                       "potential_topics"],
                            "type": "best_fields",
                            "minimum_should_match": "50%"
                        }
                    },
                    "filter": {
                        "bool": {
                            "must": request.session.get('filters')
                        }
                    }
                }
            },
            "aggs": aggregares
        }

        result = es.search(index="dataset", body=query_body)

    lstResults = []
    LocationspatialCoverage = []
    spatialCounter = 0
    for searchResult in result['hits']['hits']:
        lstResults.append(searchResult['_source'])
        for potentialocation in searchResult['_source']['spatial_coverage']:
            location = re.sub(r'[^A-Za-z0-9 ]+', '', potentialocation)
            if (location != "") and (location != "None") and (len(location) < 20) and (
                    location not in LocationspatialCoverage) and (spatialCounter < 10):
                spatialCounter = spatialCounter + 1
                geoLocation = {"location": location, "RI": searchResult['_source']['repo'][0]}
                LocationspatialCoverage.append(geoLocation)

    # ......................
    repo = []
    spatial_coverage = []
    theme = []
    publisher = []
    instrument = []
    # ......................
    for searchResult in result['aggregations']['repo']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != "Unknown" and
                searchResult['key'] != "Data" and searchResult['key'] != "Unspecified" and searchResult['key'] != "" and
                searchResult['key'] != "N/A"):
            RI = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            repo.append(RI)
    # ......................
    for searchResult in result['aggregations']['spatial_coverage']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != "Unknown" and
                searchResult['key'] != "Data" and searchResult['key'] != "Unspecified" and searchResult[
                    'key'] != "N/A" and searchResult['key'] != "" and ("ANE" not in searchResult['key']) and (
                        "Belgian" not in searchResult['key']) and ("calculated BB" not in searchResult['key']) and int(
                        searchResult['doc_count'] > 1)):
            SC = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            spatial_coverage.append(SC)
        # ......................
    for searchResult in result['aggregations']['theme']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != "Unknown" and
                searchResult['key'] != "Data" and searchResult['key'] != "Unspecified" and searchResult[
                    'key'] != "N/A" and searchResult['key'] != "" and int(searchResult['doc_count'] > 1)):
            Th = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            theme.append(Th)
    # ......................
    for searchResult in result['aggregations']['publisher']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != "Unknown" and
                searchResult['key'] != "Data" and searchResult['key'] != "Unspecified" and searchResult[
                    'key'] != "N/A" and searchResult['key'] != "" and int(searchResult['doc_count'] > 1)):
            Pub = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            publisher.append(Pub)
    # ......................
    for searchResult in result['aggregations']['instrument']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != "Unknown" and
                searchResult['key'] != "Data" and searchResult['key'] != "Unspecified" and searchResult[
                    'key'] != "N/A" and searchResult['key'] != "" and int(searchResult['doc_count'] > 1)):
            meT = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            instrument.append(meT)
    # ......................
    facets = {
        'repo': repo,
        'spatial_coverage': spatial_coverage,
        'theme': theme,
        'publisher': publisher,
        'instrument': instrument
    }

    # envri-statics
    # print("Got %d Hits:" % result['hits']['total']['value'])
    # return JsonResponse(result, safe=True, json_dumps_params={'ensure_ascii': False})

    numHits = result['hits']['total']['value']

    upperBoundPage = round(np.ceil(numHits / 10) + 1)
    if (upperBoundPage > 10):
        upperBoundPage = 11

    result = {
        "facets": facets,
        "results": lstResults,
        "NumberOfHits": numHits,
        "page_range": list(range(1, upperBoundPage)),
        "cur_page": (page / 10 + 1),
        "searchTerm": term,
        "functionList": getAllfunctionList(request),
        "spatial_coverage": LocationspatialCoverage
    }

    return result


# -----------------------------------------------------------------------------------------------------------------------
def synonyms(term):
    response = requests.get('https://www.thesaurus.com/browse/{}'.format(term))
    soup = BeautifulSoup(response.text, 'html.parser')
    soup.find('section', {'class': 'css-191l5o0-ClassicContentCard e1qo4u830'})
    return [span.text for span in soup.findAll('a', {'class': 'css-1kg1yv8 eh475bn0'})]


# -----------------------------------------------------------------------------------------------------------------------
def potentialSearchTerm(term):
    spell = SpellChecker()
    search_term = term.split()
    alternative_search_term = ""
    for sTerm in search_term:
        alter_word = spell.correction(sTerm)
        if alter_word:
            alternative_search_term = alternative_search_term + " " + alter_word

    alternative_search_term = alternative_search_term.rstrip()
    alternative_search_term = alternative_search_term.lstrip()

    if alternative_search_term == term:
        alternative_search_term = ""
        for sTerm in search_term:
            syn = synonyms(sTerm)
            if len(syn) > 0:
                alter_word = syn[0]
                alternative_search_term = alternative_search_term + " " + alter_word

    alternative_search_term = alternative_search_term.rstrip()
    alternative_search_term = alternative_search_term.lstrip()

    return alternative_search_term


# -----------------------------------------------------------------------------------------------------------------------
def getAllfunctionList(request):
    if not 'BasketURLs' in request.session or not request.session['BasketURLs']:
        request.session['BasketURLs'] = []
    if not 'MyBasket' in request.session or not request.session['MyBasket']:
        request.session['MyBasket'] = []

    functionList = ""
    saved_list = request.session['MyBasket']
    for item in saved_list:
        functionList = functionList + r"modifyCart({'operation':'add','type':'" + item['type'] + "','title':'" + item[
            'title'] + "','url':'" + item['url'] + "','id':'" + item['id'] + "' });"
    return functionList



class StandardAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            term = request.GET['term']
        except:
            term = ''

        try:
            page = request.GET['page']
        except:
            page = 0

        try:
            filter = request.GET['filter']
        except:
            filter = ''

        try:
            facet = request.GET['facet']
        except:
            facet = ''

        searchResults = getSearchResults(request, facet, filter, page, term)

        searchResults['suggestedSearchTerm'] = ''
        if searchResults['NumberOfHits'] == 0:
            suggestedSearchTerm = potentialSearchTerm(term)
            suggestedResults = getSearchResults(request, facet, filter, page, suggestedSearchTerm)
            if suggestedResults["NumberOfHits"] > 0:
                searchResults["suggestedSearchTerm"] = suggestedSearchTerm

        searchResults['base_path'] = base_path
        return Response(searchResults, status=status.HTTP_200_OK)
        #return render(request, 'dataset_results.html', searchResults)

