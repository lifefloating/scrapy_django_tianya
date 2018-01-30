'''
全量爬取
'''

import scrapy
import logging
import re
import redis
from bots.tianya_spider.tianya_spider.items import StoryItem
import random

redis_db = redis.Redis(host='localhost', port=6379, db=0)  # 连接redis
redis_data_dict = "links_url"
urllist = []


class TianyaFullSpider(scrapy.Spider):
    name = "tianyafull"
    allowed_domains = ['tianya.cn']
    meta = {
        'dont_redircet': True,  # 禁止网页重定向
        'handle_httpstatus_list': [301, 302]  # 对301 302处理
    }

    def start_requests(self):
        for url in redis_db.hkeys(redis_data_dict):  # 取name中所有hash的key值
            # 这里修改过了 原方案是hget==1标记已经爬取过list里面给他remove掉 如果不对就改回之前的
            if redis_db.hget(redis_data_dict, url) == b'0':  # 链接没有爬取
                url_str = str(url, encoding='utf-8')
                urllist.append(url_str)
        print(len(urllist))
        # if len(urllist) != 0:
        random.shuffle(urllist)
        for unlink in urllist:
            yield scrapy.Request(url=unlink, callback=self.parse, errback=self.parse_back, dont_filter=True,
                                 meta=self.meta)
        # 这里redis用的没起到实际效果，暂时没想到解决方案
        # else:
        # print("Complete")

    def parse(self, response):
        if response.status != 200:
            print('STATUS NOT 200')
            return
        # 帖子的作者 若此是空字符串说明是问答贴，drop
        author = "".join(
            response.xpath('//div[@id="post_head"]/div/div/span/a/@uname').extract()).strip()
        # authorid用于标识楼主的内容
        logging.info(author)
        authorid = "".join(response.xpath('//div[@id="post_head"]/div/div/span/a/@uid').extract())
        page = (response.url.split('-')[-1].split('.')[0])  # 现在str类型 标识帖子链接号 str
        story_mark = "-".join(response.url.split('-')[0:-1]).strip()  # 帖子标识用于查询
        logging.info(story_mark)
        if len(authorid) > 0:
            contenttmp = response.xpath(
                '//div/div[@*={}]//div[starts-with(@class,"bbs-content")]'.format(authorid)).extract()
            if len(contenttmp) > 0:
                pageorder = 0  # 用于判断帖子顺序
                for col in contenttmp:
                    storyitem = StoryItem()
                    storyitem["story_title"] = "".join(
                        response.xpath('//div/h1//span//text()').extract()).strip()  # 帖子标题
                    storyitem["story_author"] = author
                    storyitem["story_author_id"] = authorid
                    # 帖子发布时间
                    story_posttime = "".join(
                        response.xpath('//div[@id="post_head"]/div/div/span[2]//text()').re('\d\S.*')).strip()
                    storyitem["story_posttime"] = story_posttime  # 帖子发布时间
                    pageorder += 1
                    pagetemp = int(page)
                    story_order = pagetemp * 1000 + pageorder  # 这里记得改order*1000+page 每页不可能超过100章节
                    story_link = response.url + '-part{}'.format(pageorder)
                    storyitem["story_order"] = story_order  # 帖子顺序
                    storyitem["story_mark"] = story_mark  # 帖子标识
                    storyitem["story_link"] = story_link  # 帖子唯一链接
                    col_no_br = col.replace(r'<br>', '\n')  # 替换<br>
                    content = re.sub(r'</?\w+[^>]*>', '', col_no_br)  # 去掉html标签
                    content_len = "".join(content).strip().replace('\t', '')
                    if len(content_len) < 20:
                        storyitem["story_content"] = "Useless"  # 内容字符过少视为无用内容
                    else:
                        storyitem["story_content"] = content  # 帖子每章节的内容
                        yield storyitem
                        print(storyitem)
                        logging.info(storyitem)
                    redis_db.hset(redis_data_dict, response.url, 1)
            else:
                redis_db.hset(redis_data_dict, response.url, 1)  # 这里else处理的是待抓取页面作者没有发任何帖子

    def parse_back(self, response):
        print("Entry parse Failed")
