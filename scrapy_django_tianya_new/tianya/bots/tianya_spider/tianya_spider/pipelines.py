# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from .items import *
import os

checkFile = 'isRunning.txt'


class StatusPipeline(object):
    def open_spider(self, spider):
        if spider.name == 'tianya':
            f = open(checkFile, 'w')  # 创建文件代表爬虫正在执行
            f.close()

    def close_spider(self, spider):
        isFileExist = os.path.isfile(checkFile)  # 结束删除标识文件
        if isFileExist:
            os.remove(checkFile)


class LinksItemPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, LinksItem):
            try:
                item.save()
            except:
                raise DropItem('Links Duplicate')  # 回复帖子在上次的页面上回复的 会在抓取到这个页面，链接不存
        return item


class StoryItemPipeline(object):
    def process_item(self, item, spider):
        # 帖子的作者 若此是空字符串说明是问答贴，drop
        if isinstance(item, StoryItem):
            if item["story_author"] == "":
                raise DropItem('Useless item found!')
            elif item["story_content"] == "Useless":
                raise DropItem('Useless item found!')
            try:
                item.save()
            except:
                raise DropItem('save failed')
        return item
