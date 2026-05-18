from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework import status
# Create your views here.



# New imports from the original websarch
import json
import os
import re
import uuid
from urllib.parse import urlparse

import dateutil.parser
import ijson
import nltk
import numpy as np
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponseBadRequest
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Index
from spellchecker import SpellChecker

nltk.download('words')


# elasticsearch_url = os.environ['ELASTICSEARCH_URL']
# elasticsearch_username = os.environ.get('ELASTICSEARCH_USERNAME')
# elasticsearch_password = os.environ.get('ELASTICSEARCH_PASSWORD')

# # Nafis: Updated by nafis , hardcoded for now
# elasticsearch_username = "elastic"
# #os.environ.get('ELASTICSEARCH_USERNAME')
# elasticsearch_password = "3g53NNL+Xusi3yzEV+Od"
# #os.environ.get('ELASTICSEARCH_PASSWORD')
# if elasticsearch_username and elasticsearch_password:
#     http_auth = [elasticsearch_username, elasticsearch_password]
# else:
#     http_auth = None



    

#base_path = os.environ.get('BASE_PATH').strip()
base_path = "search"

words = set(nltk.corpus.words.words())
ResearchInfrastructures = {
    'icos-cp.eu': {
        'id': 1,
        'url': 'https://www.icos-cp.eu/',
        'label': 'Multi-domain',
        'title': 'Integrated Carbon Observation System',
        'acronym': 'ICOS'
    },
    'seadatanet.org': {
        'id': 2,
        'url': 'https://www.seadatanet.org/',
        'label': 'Marine',
        'title': 'Pan-European infrastructure for ocean and marine data management',
        'acronym': 'SeaDataNet'
    },
    'lifewatch.eu': {
        'id': 3,
        'url': 'https://www.lifewatch.eu/',
        'label': 'Multi-domain',
        'title': 'An e-Infrastructure for basic research on biodiversity and ecosystems',
        'acronym': 'LifeWatch'
    },
    'anaee.eu': {
        'id': 4,
        'url': 'https://www.anaee.eu/',
        'label': 'Terrestrial ecosystem / Biodiversity',
        'title': 'Analysis and Experimentation on Ecosystems',
        'acronym': 'AnaEE'
    },
    'actris.eu': {
        'id': 5,
        'url': 'https://www.actris.eu/',
        'label': 'Atmospheric',
        'title': 'The Aerosol, Clouds and Trace Gases Research Infrastructure',
        'acronym': 'ACTRIS'
    },
    'aquacosm.eu': {
        'id': 6,
        'url': 'https://www.aquacosm.eu/',
        'label': 'Marine / Freshwater',
        'title': 'EU network of mesocosms facilities for research on marine and freshwater',
        'acronym': 'AQUACOSM'
    },
    'arise-project.eu': {
        'id': 7,
        'url': 'http://arise-project.eu/',
        'label': 'Atmosphere',
        'title': 'Atmospheric dynamics Research InfraStructure in Europe',
        'acronym': 'ARISE'
    },
    'danubius-pp.eu': {
        'id': 8,
        'url': 'https://danubius-pp.eu/',
        'label': 'River / Marine',
        'title': 'Preparatory Phase For The Paneuropean Research Infrastructure',
        'acronym': 'DANUBIUS-RI'
    },
    'dissco.eu': {
        'id': 9,
        'url': 'https://www.dissco.eu/',
        'label': 'Terrestrial ecosystem / Biodiversity',
        'title': 'Distributed System of Scientific Collections',
        'acronym': 'DiSSCo'
    },
    'eiscat.se': {
        'id': 10,
        'url': 'https://eiscat.se/',
        'label': 'Atmospheric',
        'title': 'EISCAT Scientific Association',
        'acronym': 'EISCAT 3D'
    },
    "elter-ri.eu": {
        "id": 11,
        "url": "https://elter-ri.eu/",
        "domain": "Biodiversity / Ecosystems",
        "title": "Long-Term Ecosystem Research in Europe",
        "acronym": "eLTER RI"
    },
    'embrc.eu': {
        'id': 12,
        'url': 'https://www.embrc.eu/',
        'label': 'Marine / Biodiversity',
        'title': 'Long-Term Ecosystem Research in Europe',
        'acronym': 'EMBRC'
    },
    'emso.eu': {
        'id': 13,
        'url': 'https://emso.eu/',
        'label': 'Multi-domain',
        'title': 'European Multidisciplinary Seafloor and water column Observatory',
        'acronym': 'EMSO'
    },
    'emphasis.plant-phenotyping.eu': {
        'id': 14,
        'url': 'https://emphasis.plant-phenotyping.eu/',
        'label': 'Terrestrial Ecosystem',
        'title': 'European Infrastructure for Plant Phenotyping',
        'acronym': 'EMPHASIS'
    },
    'epos-eu.org': {
        'id': 15,
        'url': 'https://www.epos-eu.org/',
        'label': 'Solid Earth Science',
        'title': 'European Plate Observing System',
        'acronym': 'EPOS'
    },
    'eufar.net': {
        'id': 16,
        'url': 'https://www.eufar.net/',
        'label': 'Atmospheric',
        'title': 'The EUropean Facility for Airborne Research',
        'acronym': 'EUFAR'
    },
    'euro-argo.eu': {
        'id': 17,
        'url': 'https://www.euro-argo.eu/',
        'label': 'Marine',
        'title': 'European Research Infrastructure Consortium for observing the Ocean',
        'acronym': 'Euro-Argo ERIC'
    },
    'eurofleet.fr': {
        'id': 18,
        'url': 'https://www.eurofleet.fr/',
        'label': 'Marine',
        'title': 'An alliance of European marine research infrastructure to meet the evolving needs of the research and industrial communities',
        'acronym': 'EUROFLEETS+'
    },
    'eurogoos.eu': {
        'id': 19,
        'url': 'https://eurogoos.eu/',
        'label': 'Marine',
        'title': 'European Global Ocean Observing System',
        'acronym': 'EuroGOOS'
    },
    'eurochamp.org': {
        'id': 20,
        'url': 'https://www.eurochamp.org/',
        'label': 'Atmospheric',
        'title': 'Integration of European Simulation Chambers for Investigating Atmospheric Processes',
        'acronym': 'EUROCHAMP'
    },
    'hemera-h2020.eu': {
        'id': 21,
        'url': 'https://www.hemera-h2020.eu/',
        'label': 'Atmospheric',
        'title': 'Integrated access to balloon-borne platforms for innovative research and technology',
        'acronym': 'HEMERA'
    },
    'iagos.org': {
        'id': 22,
        'url': 'https://www.iagos.org/',
        'label': 'Atmospheric',
        'title': 'In Service Aircraft for a Global Observing System',
        'acronym': 'IAGOS'
    },
    'eu-interact.org': {
        'id': 23,
        'url': 'https://eu-interact.org/',
        'label': 'Terrestrial Ecosystem',
        'title': 'Building Capacity For Environmental Research And Monitoring In Arctic And Neighbouring Alpine And Forest Areas',
        'acronym': 'INTERACT'
    },
    'is.enes.org': {
        'id': 24,
        'url': 'https://is.enes.org/',
        'label': 'Multi-domain',
        'title': 'Infrastructure For The European Network For Earth System Modelling Enes',
        'acronym': 'IS-ENES'
    },
    'jerico-ri.eu': {
        'id': 25,
        'url': 'https://www.jerico-ri.eu/',
        'label': 'Marine',
        'title': 'The European Integrated Infrastructure For In Situ Coastal Observation',
        'acronym': 'JERICO-RI'
    },
    'sios-svalbard.org': {
        'id': 26,
        'url': 'https://www.sios-svalbard.org/',
        'label': 'Multi-domain',
        'title': 'Svalbard integrated Earth observing system',
        'acronym': 'SIOS'
    }
}
aggregares = {
    "locations": {
        "terms": {
            "field": "locations.keyword",
            "size": 20,
        }
    },
    "people": {
        "terms": {
            "field": "people.keyword",
            "size": 20,
        }
    },
    "organizations": {
        "terms": {
            "field": "organizations.keyword",
            "size": 20,
        }
    },
    "products": {
        "terms": {
            "field": "products.keyword",
            "size": 20,
        }
    },
    "workOfArt": {
        "terms": {
            "field": "workOfArt.keyword",
            "size": 20,
        }
    },
    "ResearchInfrastructure": {
        "terms": {
            "field": "researchInfrastructure.acronym.keyword",
            "size": 20,
        }
    },
    "files": {
        "terms": {
            "field": "files.extension.keyword",
            "size": 20,
        }
    }
}


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


def getSearchResults(request, facet, filter, searchtype, page, term):
    
    # Nafis Updated Elastic
    # es = Elasticsearch([{'host': 'localhost', 'port': 9200, "scheme": "https"}], http_auth=http_auth, ca_certs="/home/ubuntu/test/indexer/web_indexers/http_ca.crt")
    # es = Elasticsearch(
    # "https://lifewatch.lab.uvalight.net/es-nafis/",
    # http_auth=("elastic", "otwVzERILUVxDb090WBJoh56WTFFT8cT"),
    # verify_certs=False)
    # #es = Elasticsearch(elasticsearch_url, http_auth=[elasticsearch_username, elasticsearch_password])
    # if es.ping():
    #         print("Connected to Elasticsearch")
    # else:
    #     print("Could not connect to Elasticsearch")
    #     #verify_certs=False
    #     print("Printing ping and information*****", es.ping())
    #     print(es.info())

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
 
    
    index = Index('webcontents', es)

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
            index="webcontents",
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
                            "fields": ["title", "pageContetnts", "organizations", "topics",
                                       "people", "workOfArt", "files", "locations", "dates",
                                       "researchInfrastructure"],
                            "type": "best_fields",
                            "minimum_should_match": "100%"
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
        result = es.search(index="webcontents", body=query_body)

    lstResults = []
    lstImageFilename = []
    lstImageURL = []

    for searchResult in result['hits']['hits']:
        lstResults.append(searchResult['_source'])

        # Shittiest piece of code in the world
        # Shit to cover up a massive shit
        #print("printing shit", searchResult['_source'])
        searchResult['_source']["pageContents"] = searchResult['_source']["pageContetnts"]
        # biggest coverup in the history of programming
        # If someone is impressed, please say Hi at pialcsedu19@gmail.com


        lstResults.append(searchResult['_source'])

        if (searchtype == "imagesearch"):
            url = searchResult['_source']['url']
            ResearchInfrastructure = searchResult['_source']['researchInfrastructure']
            for img in searchResult['_source']['images']:
                a = urlparse(img)
                filename = os.path.basename(a.path)
                extension = os.path.splitext(filename)[1]
                filenameWithoutExt = os.path.splitext(filename)[0]
                if filename not in lstImageFilename:
                    lstImageFilename.append(filename)
                    image = {'imageURL': img, 'imageWebpage': url[0], 'filename': filenameWithoutExt,
                             'extension': extension, 'ResearchInfrastructure': ResearchInfrastructure[0]}
                    lstImageURL.append(image)
    # ......................
    files = []
    locations = []
    people = []
    organizations = []
    workOfArt = []
    products = []
    ResearchInfrastructure = []
    # ......................
    for searchResult in result['aggregations']['ResearchInfrastructure']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != "" and
                searchResult['key'] != "KB"):
            RI = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            ResearchInfrastructure.append(RI)
    # ......................
    for searchResult in result['aggregations']['locations']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != ""):
            loc = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            locations.append(loc)
    # ......................
    for searchResult in result['aggregations']['people']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != ""):
            prod = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            people.append(prod)
    # ......................
    for searchResult in result['aggregations']['organizations']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != ""):
            org = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            organizations.append(org)
    # ......................
    for searchResult in result['aggregations']['products']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != ""):
            pers = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            products.append(pers)
    # ......................
    for searchResult in result['aggregations']['workOfArt']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != ""):
            auth = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            workOfArt.append(auth)
    # ......................
    for searchResult in result['aggregations']['files']['buckets']:
        if (searchResult['key'] != "None" and searchResult['key'] != "unknown" and searchResult['key'] != ""):
            ext = {
                'key': searchResult['key'],
                'doc_count': searchResult['doc_count']
            }
            files.append(ext)
    # ......................

    facets = {
        "files": files,
        "locations": locations,
        "workOfArt": workOfArt,
        "organizations": organizations,
        "people": people,
        "products": products,
        "ResearchInfrastructure": ResearchInfrastructure
    }
    # envri-statics
    # print("Got %d Hits:" % result['hits']['total']['value'])
    # return JsonResponse(result, safe=True, json_dumps_params={'ensure_ascii': False})
    numHits = result['hits']['total']['value']

    upperBoundPage = round(np.ceil(numHits / 10) + 1)
    if (upperBoundPage > 10):
        upperBoundPage = 11

    results = {
        "facets": facets,
        "results": lstResults,
        "NumberOfHits": numHits,
        "page_range": list(range(1, upperBoundPage)),
        "cur_page": (page / 10 + 1),
        "searchTerm": term,
        "functionList": getAllfunctionList(request),
        "lstImageURL": lstImageURL
    }

    print("Type of results of web search ... ... ...", type(results))

    return results

def synonyms(term):
    response = requests.get('https://www.thesaurus.com/browse/{}'.format(term))
    soup = BeautifulSoup(response.text, 'html.parser')
    soup.find('section', {'class': 'css-191l5o0-ClassicContentCard e1qo4u830'})
    return [span.text for span in soup.findAll('a', {'class': 'css-1kg1yv8 eh475bn0'})]



class StandardAPIView(APIView):

    def get(self, request, *args, **kwargs):
        print("Responding from get ... ... ...", request.data)


        print("You are at the landing page of web search...")
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
            searchtype = request.GET['searchtype']
        except:
            searchtype = 'websearch'

        try:
            filter = request.GET['filter']
        except:
            filter = ''

        try:
            facet = request.GET['facet']
        except:
            facet = ''

        print("Nafis: Printing Search Parameters", request, facet, filter, searchtype, page, term)
        searchResults = getSearchResults(request, facet, filter, searchtype, page, term)

        searchResults['suggestedSearchTerm'] = ''
        if searchResults['NumberOfHits'] == 0:
            suggestedSearchTerm = potentialSearchTerm(term)
            suggestedResults = getSearchResults(request, facet, filter, searchtype, page, suggestedSearchTerm)
            if suggestedResults["NumberOfHits"] > 0:
                searchResults["suggestedSearchTerm"] = suggestedSearchTerm

        if searchtype == 'imagesearch':
            htmlrender = 'imagesearch_results.html'
        else:
            htmlrender = 'webcontent_results.html'

        searchResults['base_path'] = base_path

        print("Printing the type of searchresults", type(searchResults))
        #------------------
        #return searchResults
        #print(searchResults)
        return Response(searchResults, status=status.HTTP_200_OK)
        #return Response({'data' : searchResults}, status=status.HTTP_200_OK)