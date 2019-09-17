# from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from newsaggregator.serializers import NewsSerializer
from newsaggregator.models import NewsCollector

@api_view(['GET'])
def news_list(request):
    query = None
    if 'query' in request.GET.keys() and request.GET['query']: query = request.GET['query']
    news = NewsCollector().fetch_news(query)
    results = NewsSerializer(news, many=True).data
    return Response(results)
