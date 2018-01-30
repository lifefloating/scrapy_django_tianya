from django.db import models

# Create your models here.
# Create your models here.
from django.db import models

'''首页的故事表 '''


class Story(models.Model):
    story_title = models.CharField(max_length=100, null=True)  # 帖子标题
    story_author = models.CharField(max_length=50, null=True)  # 帖子作者
    story_author_id = models.CharField(max_length=20, null=True)  # 作者id
    story_order = models.IntegerField(null=True)  # 页码和帖子顺序组成 筛选顺序
    story_mark = models.CharField(max_length=100, null=True)  # 帖子标识
    story_link = models.CharField(max_length=100, unique=True, null=True)  # 帖子链接一页多个帖子
    story_posttime = models.CharField(max_length=50, null=True)  # 帖子发布时间
    story_content = models.TextField()  # 帖子内容

    class Meta:
        app_label = 'tianyadata'
        db_table = 'tianya_story'  # 数据库表名为tianya_story
        index_together = [
            ["story_mark", "story_order"],
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
