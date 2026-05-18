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
    



# Create your views here.
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

        print("You are here ...")
        #searchResults = getSearchResults(request, facet, filter, page, term)
        searchResults = []
        searchResults['suggestedSearchTerm'] = ''
        # if searchResults['NumberOfHits'] == 0:
        #     suggestedSearchTerm = potentialSearchTerm(term)
        #     suggestedResults = getSearchResults(request, facet, filter, page, suggestedSearchTerm)
        #     if suggestedResults["NumberOfHits"] > 0:
        #         searchResults["suggestedSearchTerm"] = suggestedSearchTerm

        searchResults['base_path'] = base_path
        return Response(searchResults, status=status.HTTP_200_OK)
        #return render(request, 'dataset_results.html', searchResults)

# http://145.100.135.115:8002/searchall/search?term=sea+surface+temperature&page=1