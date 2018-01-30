'''对url标记0为为爬取，爬取后标记为1 存入redis，每次从redis中取value为0的url'''
import redis
from django.db import connection
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tianya.settings")
django.setup()

redis_db = redis.Redis(host='localhost', port=6379, db=0)  # 连接redis
redis_data_dict = "links_url"

# redis_db.flushdb()  # 删除全部key 每次全量之前先清空

cursor = connection.cursor()  # 建立连接
cursor.execute('SELECT links FROM tianya_links')  # sql语句
rows = cursor.fetchall()
count = 0
for url in rows:  # 全部url rows tuple类型
    count += 1
    print(url[0])
    try:
        redis_db.hset(redis_data_dict, url[0], 0)  # 把每条url写入redis 并且将value设置为0
    finally:
        pass
print('save ok')
print('url nums={}'.format(count))
