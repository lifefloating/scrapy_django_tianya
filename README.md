# scrapy_django_tianya
[![OSCS Status](https://www.oscs1024.com/oscs_api/v2/badge/lifefloating/scrapy_django_tianya.svg?size=small)](https://www.oscs1024.com/repo/lifefloating/scrapy_django_tianya?ref=badge_small)
天涯 tianya - Scrapy+Django 增量抓取天涯莲蓬鬼话
<br>
目标网址[莲蓬鬼话](http://bbs.tianya.cn/list-16-1.shtml)
<br>

## Scrapy文档
bi~传送门[scrapy官方文档1.4.0](https://docs.scrapy.org/en/latest/)
## Django文档
bi~传送门[django文档](https://docs.djangoproject.com/en/2.0/)
## 主要过程
    * scrapy+django环境搭建
    * 数据库结构设计
    * scrapy代码实现 去重与增量
    * 反爬策略
    * 数据用于django页面的展示
    * 部署至centos 周期性抓取 (虚拟机暂时熟悉下部署流程)     
    
### Scrapy+Django环境搭建
>这里用Django的modes层来作为scrapy的item定义
<br>
   网上有很多关于这种教程推荐看下：http://blog.csdn.net/clayanddev/article/details/53768975
<br>
<br>

* 环境配置
<br>
 google!
 <br>
  django和scrapy改怎么搞怎么搞不介绍过多，重点是下面的一段，不然很可能按照上面教程走下来无法完成环境搭建
 <br>
 <br>
  在spider文件夹同级目录下的__init__.py文件里加上下面代码：
 <br>
  import os, sys, django
 <br>
  sys.path.append(r'E:\PythonProject\scrapy_django_tianya2\tianya')  # `填你的django项目路径`
 <br>
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tianya.settings")  # django项目.settings
 <br>
 django.setup()
 <br>
 <br>
  这样大体环境搭建完成!
 <br>
 <br>
  
### 数据库设计
<br>
   代码在Django的Models.py那里
<br>
   需要注意的是story表的话story_link 唯一索引 story_mark,story_order联合索引
<br>
   这里的联合索引是后面数据查询的必要条件，因为数据量略大story表100多w数据，查询条件还是加个索引
<br>
<br>

  #### 数据库表数据概略
  <br>
  tianya_index表
  <br>
  
![](https://github.com/DANTE0206/scrapy_django_tianya/blob/master/imgs/tianya_index.jpg)
  
  tianya_story表 目前103w的帖子
  
![](https://github.com/DANTE0206/scrapy_django_tianya/blob/master/imgs/tianya_story.jpg)
   
   tianya_story表 目前103w的帖子
   
![](https://github.com/DANTE0206/scrapy_django_tianya/blob/master/imgs/tianya_index.jpg)

### scrapy代码实现 去重与增量

  我讲下思路和流程吧，因为代码注释很全了已经。
  <br>
  <br>
  * 全量以及去重
   <br>
      *   目标网址是天涯的莲蓬鬼话全部帖子的章节，首先可以先做一次全量，虽然可能不全，但是无妨
   <br>
      先把全部帖子的全部url抓下来，xpath找到首页全部url，找到下一页，如此直到没有下一页为止，url的入口链接已经基本拿到
   <br>
   <br>
      每个url一个主题帖，里面有很多个页，每一页有多个章节，多页的url可以通过抓取最后一页的url再去拼接出全部url
   <br>
      拿到全部url之后，再写个spider去处理这些url的帖子item，这个时候可以考虑多进程，所以这里需要去重，多个进程去取url跑
   <br>
      难免会有重复的，跑之前取到的url先random.shuffle一下，这里去重方案我是将全部url取出放置Redis，
   <br>
      每当爬取或者因为需要丢弃这个url，这个url再Redis中对于的value改为1，没有爬取的value为0，每次只从value为0的中取key作为url
   <br>
      其实这里有缺陷，就是效率问题，如果有更好方案希望私我，scrapy-redis暂时不考虑
  <br>
  <br>
  
  * 增量与去重
   <br>
      *   增量 对比回复时间与上次的回复时间，判断是否更新
   <br>
      首页的url和story_index表中story_link_main`比较`如果他存在与说明不是全新的帖子
   <br>
      这里与数据库交互一次，顺带说下django自带的数据库驱动是MySQLdb暂时不支持python3.6的，我使用的pymysql
   <br>
      在你的Django项目同名文件夹里面的__init__.py文件中添加如下代码(这里就是tianya下面的__init__.py)：
      <br>
      import pymysql
      <br>
      pymysql.install_as_MySQLdb()
   <br>
   <br>
      index只`更新`时间，帖子从后面开始抓取5页比较，这里是为了减少爬取量，不排除可能有漏掉的情况
   <br>
      这里也与数据库交互一次
   <br>
      否则是全新的帖子，从最后一页开始全部抓取
  <br>
  <br>
    
### 反爬策略
   <br>
      反爬策略有很多，但是无非都是在中间件那里做一些处理cookie, ua useragent,ip池代理，以及settings.py的相关参数设置，都是模拟浏览器行为
    <br>
    网上同样有资料可以参考：http://blkstone.github.io/2016/03/02/crawler-anti-anti-cheat/ 等
    <br>
    莲蓬鬼话并没有要求验证码或者登陆之类的，我只是加了个useragent代理，本来想加个ip代理，但是没有发现可用的ip，卒。
    <br>
    
### Django页面的编写
  这里的页面实现不复杂，Django了解的人应该可以看懂，唯一查询中不要用like这里，之前我用了，不建议用
  <br>
  我这里用了bootstrap的样式，在static静态文件中引入就好。
  <br>

### 部署至centos
  centos上的文件为centos_file_main，静态文件被我删了，太多，在centos上部署需要注意数据库相关的地方url需要修改
  <br>
  一些配置文件也上传至此，部署时，我自己的注意点在txt文件中。
  <br>
  部署我参考了两个教程，非常感谢这些乐于分享的人
  <br>
  centos下配置django、uwsgi和nginx http://blog.csdn.net/chenkfkevin/article/details/78297666
  <br>
  centos7下采用Nginx+uwsgi来部署django https://www.cnblogs.com/sumoning/p/7147755.html
  <br>
  supervisor 从安装到使用 https://www.jianshu.com/p/3658c963d28b
 
### Django项目图片
<br>

* 首页
 <br>
 
 ![](https://github.com/DANTE0206/scrapy_django_tianya/blob/master/imgs/index.jpg)
 <br>
 
 * 首页分页
 <br>
 
 ![](https://github.com/DANTE0206/scrapy_django_tianya/blob/master/imgs/index_pages.jpg)
 * 详细页
 <br>
 
 ![](https://github.com/DANTE0206/scrapy_django_tianya/blob/master/imgs/detail.jpg)
 * 详细页分页
 <br>
 
 ![](https://github.com/DANTE0206/scrapy_django_tianya/blob/master/imgs/detail_pages.jpg)
 
 
 ### 之前方案已经删除，新版本scrapy_django_tianya_new
 <br>
 
* 修改思路

     <br>
      之前的方案是按照比对时间，给每段故事的章节拼接一个唯一的标记url，虽然顺序可以保证一致，但是不排除其他特殊情况顺序会错，
     <br>
      现在发现原帖中已经有这样的标记，replyid，加上时间既可以标记唯一顺序，对每段内容做md5，在一定时间范围内的故事更新比对其md5
     <br>
      正常比对时间就行，以上比对的方案是用于有些内容作者在上次帖中更新。
 
