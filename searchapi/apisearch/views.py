# Basic Imports
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework import status


# Functional Imports
import os
import numpy as np
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Index
from spellchecker import SpellChecker
# Create your views here.


aggregares = {
    "category": {
        "terms": {
            "field": "category.keyword",
            "size": 20,
        }
    },
    "provider": {
        "terms": {
            "field": "provider.keyword",
            "size": 20,
        }
    },
    "serviceType": {
        "terms": {
            "field": "serviceType.keyword",
            "size": 20,
        }
    },
    "architecturalStyle": {
        "terms": {
            "field": "architecturalStyle.keyword",
            "size": 20,
        }
    },
    "sslSupprt": {
        "terms": {
            "field": "sslSupprt.keyword",
            "size": 20,
        }
    },
}

# elasticsearch_url = os.environ['ELASTICSEARCH_URL']
# elasticsearch_username = os.environ.get('ELASTICSEARCH_USERNAME')
# elasticsearch_password = os.environ.get('ELASTICSEARCH_PASSWORD')

# Nafis Updated Elastic
elasticsearch_username = "elastic"
#os.environ.get('ELASTICSEARCH_USERNAME')
elasticsearch_password = "3g53NNL+Xusi3yzEV+Od"
#os.environ.get('ELASTICSEARCH_PASSWORD')
if elasticsearch_username and elasticsearch_password:
    http_auth = [elasticsearch_username, elasticsearch_password]
else:
    http_auth = None


#base_path = os.environ.get('BASE_PATH').strip()
base_path = "search"

# NEW ES #

# -----------------------------------------------------------------------------------------------------------------------
def synonyms(term):
    response = requests.get('https://www.thesaurus.com/browse/{}'.format(term))
    soup = BeautifulSoup(response.text, 'html.parser')
    soup.find('section', {'class': 'css-191l5o0-ClassicContentCard e1qo4u830'})
    return [span.text for span in soup.findAll('a', {'class': 'css-1kg1yv8 eh475bn0'})]


def getSearchResults(request, facet, filter, page, term):
    print("You are in API SEARCH ...")
    #es = Elasticsearch(elasticsearch_url, http_auth=[elasticsearch_username, elasticsearch_password])
    #es = Elasticsearch([{'host': 'localhost', 'port': 9200, "scheme": "https"}], http_auth=http_auth, ca_certs="/home/ubuntu/test/indexer/web_indexers/http_ca.crt")
    #print("ES CREATED ...")
    
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



    index = Index('webapi', es)
    if filter != "" and facet != "":
        saved_list = request.session['filters']
        saved_list.append({"term": {facet + ".keyword": filter}})
        request.session['filters'] = saved_list
    else:
        if 'filters' in request.session:
            del request.session['filters']
        request.session['filters'] = []

    page = (int(page) - 1) * 10
    print("value of page ", page)
    result = {}
    if term == "*" or term == "top10":
        result = es.search(
            index="webapi",
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
            "from": page, "size": 10,
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": term,
                            "fields": ["name", "description", "category", "provider", "serviceType",
                                       "architecturalStyle"],
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

        result = es.search(index="webapi", body=query_body)
    lstResults = []
    for searchResult in result['hits']['hits']:
        lstResults.append(searchResult['_source'])
    # ......................
    provider = []
    category = []
    sslSupprt = []
    architecturalStyle = []
    serviceType = []
    # ......................
    for searchResult in result['aggregations']['provider']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != "Unknown" and
                searchResult['key'] != "Data" and searchResult['key'] != "Unspecified" and searchResult['key'] != ""):
            pro = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            provider.append(pro)
    # ......................
    for searchResult in result['aggregations']['category']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != "Unknown" and
                searchResult['key'] != "Data" and searchResult['key'] != "Unspecified" and searchResult['key'] != ""):
            cat = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            category.append(cat)
    # ......................
    for searchResult in result['aggregations']['sslSupprt']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != "Unknown" and
                searchResult['key'] != "Data" and searchResult['key'] != "Unspecified" and searchResult['key'] != ""):
            ssl = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            sslSupprt.append(ssl)
    # ......................
    for searchResult in result['aggregations']['architecturalStyle']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != "Unknown" and
                searchResult['key'] != "Data" and searchResult['key'] != "Unspecified" and searchResult['key'] != ""):
            arch = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            architecturalStyle.append(arch)
    # ......................
    for searchResult in result['aggregations']['serviceType']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != "Unknown" and
                searchResult['key'] != "Data" and searchResult['key'] != "Unspecified" and searchResult['key'] != ""):
            service = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            serviceType.append(service)
    # ......................
    facets = {
        'provider': provider,
        'category': category,
        'sslSupprt': sslSupprt,
        'architecturalStyle': architecturalStyle,
        'serviceType': serviceType
    }

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
        "functionList": getAllfunctionList(request)
    }
    return result


def potentialSearchTerm(term):
    spell = SpellChecker()
    search_term = term.split()
    alternative_search_term = ""
    for s_term in search_term:
        alter_word = spell.correction(s_term)
        if alter_word:
            alternative_search_term = alternative_search_term + " " + alter_word

    alternative_search_term = alternative_search_term.rstrip()
    alternative_search_term = alternative_search_term.lstrip()

    if alternative_search_term == term:
        alternative_search_term = ""
        for s_term in search_term:
            syn = synonyms(s_term)
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
    def get(self, request, *args, **Kwargs):

        
        try:
            term = request.GET['term']
            term = term.rstrip()
            term = term.lstrip()
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



        #print("Printing from API Search ... ... ...", searchResults)

        searchResults['suggestedSearchTerm'] = ''
        if searchResults['NumberOfHits'] == 0:
            suggestedSearchTerm = potentialSearchTerm(term)
            suggestedResults = getSearchResults(request, facet, filter, page, suggestedSearchTerm)
            print(suggestedSearchTerm, suggestedResults["NumberOfHits"])
            if suggestedResults["NumberOfHits"] > 0:
                searchResults["suggestedSearchTerm"] = suggestedSearchTerm

        searchResults['base_path'] = base_path
        #return render(request, 'webapi_results.html', searchResults)
        
        return Response(searchResults, status=status.HTTP_200_OK)