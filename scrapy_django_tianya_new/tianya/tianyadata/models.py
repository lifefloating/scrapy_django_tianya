from django.db import models

# Create your models here.
# Create your models here.
from django.db import models

'''首页的故事表 '''


class Story(models.Model):
    story_mark = models.CharField(max_length=100)  # 帖子标识
    story_replyid = models.IntegerField()  # 帖子每个章节的replyid 用于标识和排序
    story_title = models.CharField(max_length=100, null=True)  # 帖子标题
    story_author = models.CharField(max_length=50, null=True)  # 帖子作者
    story_author_id = models.CharField(max_length=20, null=True)  # 作者id
    story_link = models.CharField(max_length=100, unique=True, null=True)  # 帖子链接一页多个帖子
    story_posttime = models.CharField(max_length=50, null=True)  # 帖子发布时间
    story_each_reply_time = models.CharField(max_length=50, null=True)
    story_content = models.TextField()  # 帖子内容
    story_content_md5 = models.CharField(max_length=50)  # 帖子内容的md5 比较章节是否有更新

    # story_replyid 排序 /  1
    # story_mark 联合主键 filter 条件 / 1
    # 加字段 story_content_md5 /
    # 加字段 story_each_reply_time / 1

    class Meta:
        app_label = 'tianyadata'
        db_table = 'tianya_story'  # 数据库表名为tianya_story
        index_together = [
            ["story_mark", "story_replyid"],
        ]


class Index(models.Model):
    story_title = models.CharField(max_length=100, null=True)  # 帖子标题
    story_link_main = models.CharField(max_length=100, unique=True, null=True)  # 帖子链接
    story_author = models.CharField(max_length=50, null=True)  # 帖子作者
    story_replytime = models.CharField(max_length=50, null=True)  # 帖子回复时间

    class Meta:
        app_label = 'tianyadata'
        db_table = 'tianya_index'  # 表名tianya_index


'''全部链接'''


class Links(models.Model):
    links = models.CharField(max_length=100, unique=True, null=True)  # redis去重用，数据库内不能重复

    class Meta:
        app_label = 'tianyadata'
        db_table = 'tianya_links'
