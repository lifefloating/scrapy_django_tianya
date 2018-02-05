import logging
import scrapy
import time
from ..items import LinksItem

'''这个spider爬取所有帖子的主链接和全部链接
主链接单独一张表，全部链接一张表  链接数115371 78183 story
拿到主链接之后去取到最后的页码，拼接全部页码，不需要递归
保存了首页第一条故事帖的回复时间 用于后面增量的时间比较
'''


class TianyanLinkSpider(scrapy.Spider):
    name = 'tianyalinks'
    allowed_domains = ['tianya.cn']
    root_url = 'http://bbs.tianya.cn'
    start_urls = ['http://bbs.tianya.cn/list-16-1.shtml', ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
            yield scrapy.Request(url=url, callback=self.parse_lasttime)

    def parse(self, response):
        urllist = response.xpath('//div[@id="main"]/div/table/tbody/tr/td[1]/a/@href').extract()
        if len(urllist) != 0:
            for urltemp in urllist:  # 首页全部主贴链接 mainlink
                index_story_link_main = self.root_url + urltemp
                yield scrapy.Request(url=index_story_link_main, callback=self.parse_allpage)
            tmp = response.xpath('//div[@id="main"]/div/div[@class="links"]/a[@rel]/@href').extract_first()  # 下一页 str
            if tmp is not None:
                index_nextpage = self.root_url + tmp  # 主页下一页
                yield scrapy.Request(url=index_nextpage, callback=self.parse)
                logging.info(index_nextpage)

    '''# 首页故事帖的最大回复时间 用于后面增量的时间比较'''

    def parse_lasttime(self, response):
        lasttime_xpath = response.xpath('//*[@id="main"]/div[7]/table/tbody/tr/td[5]/@title').extract()  # str
        lasttime = lasttime_xpath[1]
        with open(r"E:\PythonProject\scrapy_django_tianya2\last_runtime.txt", "w+") as f:
            f.write(lasttime)

    '''从主链接xpath得到最后链接，拼接出全部url保存'''

    def parse_allpage(self, response):
        pagelist = response.xpath('//div[@id="post_head"]/div/div/form/a/@href').extract()  # 取到说明是多页
        if not pagelist:  # 没有多页这里是[] 说明只有一页
            linksitem1 = LinksItem()
            linksitem1["links"] = response.url
            linksitem1.save()
        else:  # pagelist不是[]说明多页
            last_page_temp = pagelist[len(pagelist) - 2]  # 最后一页链接 倒序切片有时候报错越界如 /post-16-1699084-22.shtml
            url_head = last_page_temp.split('-')[0:-1]  # url头
            pages = int(last_page_temp.split('-')[-1].split('.')[0])
            for i in range(1, pages + 1):
                linksitem2 = LinksItem()
                link = self.root_url + '-'.join(url_head).strip() + '-' + str(i) + '.shtml'  # 拼接出全部url 保存
                linksitem2["links"] = link
                linksitem2.save()
