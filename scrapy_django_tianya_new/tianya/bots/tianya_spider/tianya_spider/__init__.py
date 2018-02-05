import os, sys, django

sys.path.append(r'E:\PythonProject\scrapy_django_tianya2\tianya')  # 添加django项目路径到pythonpath
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tianya.settings")  # django项目.settings

django.setup()
