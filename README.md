# scrapy_django_tianya
scrapy+django增量抓取天涯莲蓬鬼话
<br>
目标网址[莲蓬鬼话](http://bbs.tianya.cn/list-16-1.shtml)
<br>
## scrapy文档
bi传送门[scrapy官方文档1.4.0](https://docs.scrapy.org/en/latest/)
## django文档
bi传送门[django文档](https://docs.djangoproject.com/en/2.0/)
## 主要过程
   <br>
    * scrapy+django环境搭建
    * 数据库结构设计
    * scrapy代码实现
    * 反爬策略
    * scrapy去重以及增量抓取的实现
    * 数据用于django页面的展示
    * 部署至centos 周期性抓取 (虚拟机暂时熟悉下部署流程)
    <br>
    
### scrapy+django环境搭建
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
   代码在django的models.py那里
<br>
   需要注意的是story表的话story_link 唯一索引 story_mark,story_order联合索引
<br>
   这里的联合索引是后面数据查询的必要条件，因为数据量略大story表100多w数据，查询条件还是加个索引
<br>
<br>

### scrapy代码实现
  <br>
  终于到了重头戏了，想想还是有点激动？
  <br>
  
![oooojbk](https://wanzao2.b0.upaiyun.com/system/pictures/213/original/%E9%9B%86%E4%B8%AD%E7%B2%BE%E7%A5%9E9.png)
  
  我讲下思路和流程吧，因为代码注释很全了已经。
  <br>
  <br>
  * 全量以及去重
   <br>
      *     目标网址是天涯的莲蓬鬼话全部帖子的章节，首先可以先做一次全量，虽然可能不全，但是无妨
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
    <br>
    *    增量 对比回复时间与上次的回复时间，判断是否更新
    <br>
    首页的url和story_index表中story_link_main`比较`如果他存在与说明不是全新的帖子
    <br>
    这里与数据库交互一次
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
    <br>
    莲蓬鬼话并没有要求验证码或者登陆之类的，我只是加了个useragent代理，本来想加个ip代理，但是没有发现可用的ip，卒。
    <br>
    
