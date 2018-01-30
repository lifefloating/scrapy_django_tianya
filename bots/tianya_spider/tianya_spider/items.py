# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem
from tianyadata.models import Story, Links, Index


# story表的item
class StoryItem(DjangoItem):
    django_model = Story


class IndexItem(DjangoItem):
    django_model = Index


class LinksItem(DjangoItem):
    django_model = Links
