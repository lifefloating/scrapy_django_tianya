import logging
import time
import scrapy
from ..items import IndexItem


class TianyaIndexSpider(scrapy.Spider):
    name = "tianyaindex"
    allowed_domains = ['tianya.cn']
    root_url = 'http://bbs.tianya.cn'
    meta = {
        'dont_redircet': True,  # 禁止网页重定向  故事具体页面页码过多有时会重定向到最后一页
        'handle_httpstatus_list': [301, 302]  # 对301 302处理
    }
    start_urls = ['http://bbs.tianya.cn/list-16-1.shtml', ]
    '''初始请求'''

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_lasttime, dont_filter=True)
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    '''将index首页的数据装入容器 这里非故事贴无法判断的只能全部，之后目录对应会有找不到对应项的'''

    def parse(self, response):
        count = 0
        for col in response.xpath('//div[@id="main"]/div/table/tbody/tr/td[1]'):  # 选取主页可见标题
            indexitem = IndexItem()
            indexitem["story_title"] = "".join(col.xpath('a//text()').extract()).strip().replace('\n', '')  # 选取标题
            urltemp = "".join(col.xpath('a/@href').extract()).strip()
            story_link_main = self.root_url + urltemp
            indexitem["story_link_main"] = story_link_main  # 帖子主链接
            story_author = response.xpath(
                '//div[@id="main"]/div/table/tbody/tr/td[2]/a//text()').extract()  # 全部author的list
            indexitem["story_author"] = story_author[count]  # 作者
            story_replytime = response.xpath(
                '//*[@id="main"]/div[7]/table/tbody/tr/td[5]/@title').extract()  # 回复时间  # 全部reply_time的list
            indexitem["story_replytime"] = story_replytime[count]  # 帖子的回复时间
            count += 1
            indexitem.save()
        tmp = response.xpath('//div[@id="main"]/div/div[@class="links"]/a[@rel]/@href').extract_first()  # 下一页 str
        if tmp is not None:
            index_nextpage = self.root_url + tmp  # 主页下一页
            yield scrapy.Request(url=index_nextpage, callback=self.parse, dont_filter=True)
            logging.info(index_nextpage)

    def parse_lasttime(self, response):  # 记录index上次抓取时间
        lasttime_xpath = response.xpath(
            '//*[@id="main"]/div[7]/table/tbody/tr/td[5]/@title').extract()  # 回复时间
        lasttime = lasttime_xpath[1]  # 最大回复时间
        with open(r"E:\PythonProject\scrapy_django_tianya2\tianya\index_runtime.txt", "w+") as f:
            f.write(lasttime)
