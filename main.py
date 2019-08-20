# coding:utf-8
import csv
import json
import pickle
import re

import requests
# from lxml import etree
# from scrapy.cmdline import execute
#
# import sys
# import os
# from urllib import parse
#
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# # execute(["scrapy", "crawl", "jobbole"])
# # execute(["scrapy", "crawl", "zhihu"])
# # execute(["scrapy", "crawl", "lagou"])
# # execute(["scrapy", "crawl", "taobao"])
# # execute(["scrapy", "crawl", "douban"])
# execute(["scrapy", "crawl", "fabang"])
# # dict = {"name": "124141",

#         "value": 12415}
# print(len(dict))
# print(dict["name"])

# str  = "显卡"
# s = parse.quote(str)
#
# print(s)
# a = ''
# # a = "u'"+a
# print(a)

# area_infos = pickle.load(open('D:/py3code/ArticleSpider/areaid.json', "rb"))
# area_list = []
# for area_info in area_infos.values():
#     for b in area_info[1:]:
#         area_list.append(b)
# count = 0
# s = []
# for i in range(len(area_list)):
#     s.append(i)
# print(sum(s))
# print(sum(range()))
# for i in area_list:
#     count += 1
    # print("抓取第%d个区域: " % count, i["regionName"], '店铺总数：', i['count'])
    # print(sum(i[]))
# totalcount = 1000
# offset = 0
# for i in range(int(totalcount/15)):
#     offset += 15
#     print(offset)

# list = []
# with open('D:/py3code/ArticleSpider/ArticleSpider/other_spider/url_parameter.csv', 'r', encoding='gb18030')as f:
#     read = csv.reader(f)
#     for i in read:
#         print(i)

#
# url_list = []
# with open("D:/py3code/ArticleSpider/ArticleSpider/other_spider/url_parameter.csv", "r", encoding="gb18030") as f:
#     read = csv.reader(f)
#     for data in read:
#         url1 = ["", ""]
#         url = 'https://meishi.meituan.com/i/poi/' + str(data[2]) + '?ct_poi=' + str(data[3])
#         url1[0] = url
#         url1[1] = data[0]
#         url_list.append(url1)
# print(url_list)

a = [21, 28, 26, 29, 31, 28, 29]
b = []
c = []
for i in range(len(a)):
    if i == len(a)-1:
        b.append(i)
        break
    if a[i+1] < a[i]:
        b.append(i)
print(b)
# print(c)