from scrapy import cmdline
import datetime
import time
import shutil
import os

recoderDir = r"crawls"  # 这是为了爬虫能够续爬而创建的目录，存储续爬需要的数据
checkFile = "isRunning.txt"  # 爬虫是否在运行的标志

startTime = datetime.datetime.now()
print(f"startTime = {startTime}")

i = 0
miniter = 0
while True:
    isRunning = os.path.isfile(checkFile)
    if not isRunning:  # 爬虫不在执行，开始启动爬虫
        # 在爬虫启动之前处理一些事情，清掉JOBDIR = crawls
        isExsit = os.path.isdir(recoderDir)  # 检查JOBDIR目录crawls是否存在
        print(f"tianya not running, ready to start. isExsit:{isExsit}")
        # fstring 3.6的新用法类似format 服务器上是3.5注意
        if isExsit:
            removeRes = shutil.rmtree(recoderDir)  # 删除续爬目录crawls及目录下所有文件
            print(f"At time:{datetime.datetime.now()}, delete res:{removeRes}")
        else:
            print(f"At time:{datetime.datetime.now()}, Dir:{recoderDir} is not exsit.")
        time.sleep(10)
        clawerTime = datetime.datetime.now()
        waitTime = clawerTime - startTime
        print(f"At time:{clawerTime}, start clawer: tianya !!!, waitTime:{waitTime}")
        cmdline.execute('scrapy crawl tianya -s JOBDIR=crawls/tianya-1'.split())
        break  # 爬虫结束之后，退出脚本
    else:
        print(f"At time:{datetime.datetime.now()}, tianya is running, sleep to wait.")
    i += 1
    time.sleep(600)  # 每10分钟检查一次
    miniter += 10
    if miniter >= 1440:  # 等待满24小时，自动退出监控脚本
        break
