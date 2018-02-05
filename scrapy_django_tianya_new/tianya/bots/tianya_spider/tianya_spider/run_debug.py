from scrapy import cmdline

'''debug用'''
name = 'tianya'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())