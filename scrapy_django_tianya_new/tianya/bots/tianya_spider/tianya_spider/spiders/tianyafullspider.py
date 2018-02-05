'''
全量爬取
'''

import scrapy
import logging
import re
import redis
from ..items import StoryItem
import random
import hashlib

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
        # else:
        # print("Complete")

    def parse(self, response):
        if response.status != 200:
            print('STATUS NOT 200')
            return
        logging.info(response.status)
        # 帖子的作者 若此是空字符串说明是问答贴，drop
        author = "".join(
            response.xpath('//div[@id="post_head"]/div/div/span/a/@uname').extract()).strip()
        # authorid用于标识楼主的内容
        logging.info(author)
        authorid = "".join(response.xpath('//div[@id="post_head"]/div/div/span/a/@uid').extract())
        story_mark = "-".join(response.url.split('-')[0:-1]).strip()  # 帖子标识用于查询
        logging.info(story_mark)
        if len(authorid) > 0:
            content_div = response.xpath('//div/div/div[starts-with(@_hostid,{})]//div'.format(authorid))  # 选取整个div
            story_each_reply_time_list = response.xpath(
                '//div/div/div[starts-with(@_hostid,{})]//div[@class="atl-info"]/span[2]//text()'.format(authorid))
            count = -1
            for col in content_div:
                contenttmp = col.xpath(
                    'div[starts-with(@class,"bbs-content")]').extract()
                contenttmp_len = "".join(contenttmp).strip()
                if len(contenttmp_len) > 0:
                    count += 1
                    replyid = int("".join(
                        col.xpath('div//@replyid').extract()).strip())  # replyid的值 需要转成int第一页第一条是没有的0
                    # story_each_reply_time = "".join(col.xpath('div/span//text()').re('\d\S.*\d')).strip()
                    if int(response.url.split('-')[-1].split('.')[0]) <= 1:
                        if count == 0:
                            story_each_reply_time = "1999-01-01 00:00:00"
                        else:
                            story_each_reply_time = "".join(
                                story_each_reply_time_list[count - 1].re('\d\S.*\d')).strip()
                    else:
                        story_each_reply_time = "".join(story_each_reply_time_list[count].re('\d\S.*\d')).strip()
                    storyitem = StoryItem()
                    storyitem["story_title"] = "".join(
                        response.xpath('//div/h1//span//text()').extract()).strip()  # 帖子标题
                    storyitem["story_author"] = author
                    storyitem["story_author_id"] = authorid
                    # 帖子发布时间
                    story_posttime = "".join(
                        response.xpath('//div[@id="post_head"]/div/div/span[2]//text()').re('\d\S.*')).strip()
                    storyitem["story_posttime"] = story_posttime  # 帖子发布时间
                    story_link = response.url + '-replyid{}'.format(replyid)
                    storyitem["story_mark"] = story_mark  # 帖子标识
                    storyitem["story_replyid"] = replyid  # replyid的值
                    storyitem["story_each_reply_time"] = story_each_reply_time  # 每个时间
                    storyitem["story_link"] = story_link  # 帖子唯一链接
                    contenttmp_no_br = contenttmp_len.replace(r'<br>', '\n')  # 替换<br>
                    content = re.sub(r'</?\w+[^>]*>', '', contenttmp_no_br)  # 去掉html标签
                    content_len = "".join(content).strip().replace('\t', '')
                    if len(content_len) < 20:
                        storyitem["story_content"] = "Useless"  # 内容字符过少视为无用内容
                    else:
                        storyitem["story_content"] = content  # 帖子每章节的内容
                    story_content_md5 = hashlib.md5(content.encode('utf-8')).hexdigest()
                    storyitem["story_content_md5"] = story_content_md5  # md5
                    yield storyitem
                    logging.info(storyitem)
                    redis_db.hset(redis_data_dict, response.url, 1)
            else:
                redis_db.hset(redis_data_dict, response.url, 1)  # 这里else处理的是待抓取页面作者没有发任何帖子

    def parse_back(self, response):
        print("Entry parse Failed")
