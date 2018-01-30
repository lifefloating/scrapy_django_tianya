from scrapy import cmdline

'''debug用'''
name = 'tianyafull'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())