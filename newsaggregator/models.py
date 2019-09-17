from django.db import models
from django.apps import apps
from django.conf import settings
import praw #Reddit python library
from newsapi import NewsApiClient
from datetime import datetime

# Create your models here.
class NewsCollector():
    def __init__(self):
        print("Collector initiated")

    def fetch_news(self, query=None):
        SOURCE_TYPE_TO_CLASS_MAP = {
            'reddit':'Reddit',
            'newsapi':'NewsAPI'
        }
        sources = NewsSource.objects.all()
        news = []
        for source in sources:
            class_name = SOURCE_TYPE_TO_CLASS_MAP[source.source_name]
            source_news = globals()[class_name](source).fetch_news(query)
            news.extend(source_news)

        #sort news by date from old to new
        from operator import itemgetter
        return sorted(news, key=itemgetter('date'), reverse=True)

SOURCES_NAMES = (
    ('reddit', 'Reddit'),
    ('newsapi', 'NewsAPI')
)

#News sources class, subclasses and managers
class RedditManager(models.Manager):
    def get_queryset(self):
        return super(RedditManager, self).get_queryset().filter(
            source_name='reddit')

class NewsAPIManager(models.Manager):
    def get_queryset(self):
        return super(NewsAPIManager, self).get_queryset().filter(
            source_name='newsapi')

class NewsSource(models.Model):
    source_name = models.CharField(max_length=200, choices=SOURCES_NAMES, unique=True)


class Reddit(NewsSource):
    objects = RedditManager()

    def fetch_news(self, query=None):
        reddit = praw.Reddit(client_id = settings.REDDIT_CLIENT_ID,
            client_secret = settings.REDDIT_SECRET,
            user_agent = settings.REDDIT_USER_AGENT,
            username = settings.REDDIT_USERNAME,
            password = settings.REDDIT_PASSWORD)
        subreddit = reddit.subreddit('news') #r/news/
        hot_news = []
        if query is None:
            hot_news = subreddit.hot(limit = 25)
        else:
            hot_news = subreddit.search(query, limit = 25)

        news_list = []
        for post in hot_news:
            news_list.append({'headline':post.title, 'link': post.url, 'source':'reddit', 'date': post.created})

        return news_list

    class Meta:
        proxy = True

class NewsAPI(NewsSource):
    objects = NewsAPIManager()

    def fetch_news(self, query=None):
        newsapi = NewsApiClient(api_key = settings.NEWS_API_KEY)
        news = []
        if query is None:
            news = newsapi.get_top_headlines(category='general', page_size=25)['articles']
        else:
            news = newsapi.get_top_headlines(q=query, category='general', page_size=25)['articles']
        return self.__convert_news(news)

    def __convert_news(self, newsapi_posts):
        news = []
        for post in newsapi_posts:
            date_string = post['publishedAt']
            format_date = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z')
            news.append({'headline':post['title'], 'link':post['url'], 'source':'newsapi', 'date':format_date.timestamp()})
        return news

    class Meta:
        proxy = True
