# coding:utf-8
import json
import time

import requests
import scrapy
from scrapy.loader import ItemLoader
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from items import DoubanDongManItem


class DouBanSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = "https://movie.douban.com"
    start_urls = "https://movie.douban.com/j/new_search_subjects?sort=U&range=0,100&tags={0}&start={1}"

# def x():
#     for i in range(0, 1000, 20):
#         return i

    def start_requests(self):
        # chrome_option = Options()
        # chrome_option.add_argument("--disable-extensions")
        # chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        #
        # browser = webdriver.Chrome(executable_path="D:/chromedriver_win32/chromedriver.exe", chrome_options=chrome_option)
        # browser.get(self.start_urls)
        # time.sleep(3)
        for i in range(0, 1000, 20):
            yield scrapy.Request(self.start_urls.format("动漫", i), callback=self.parse_url)

    def parse_url(self, response):
        data_json = json.loads(response.text)
        for i in range(len(data_json["data"])):
            single_url = data_json["data"][i]["url"]
            r = requests.get(single_url)
            itemloader = ItemLoader(item=DoubanDongManItem(), response=r)
            itemloader.add_xpath("publish_year", "//*[@id='content']/h1/span[2]/text()")
            if "all hidden" in r.text:
                itemloader.add_css("jianjie", "#link-report span.all.hidden::text")
            else:
                itemloader.add_css("jianjie", "#link-report span::text")
            itemloader.add_value("director", data_json["data"][i]["directors"])
            itemloader.add_value("title", data_json["data"][i]["title"])
            itemloader.add_value("rate", data_json["data"][i]["rate"])
            itemloader.add_value("actor", data_json["data"][i]["casts"])
            itemloader.add_value("cover_image", data_json["data"][i]["cover"])
            a = itemloader.load_item()
            yield a


            # yield scrapy.Request(single_url, callback=self.parse)

    # def parse(self, response):
    #     itemloader = ItemLoader(item=DoubanDongManItem, response=response)
    #     # itemloader.add_xpath("title", "//*[@id='content']/h1/span[1]")
    #     #         # itemloader.add_xpath("publish_year", "//*[@id='content']/h1/span[2]")
    #     #         # itemloader.add_css("director", ".subject.clearfix ")
    #     itemloader.add_css("juqingjianjie", "#link-report span::text")
    #     a = itemloader.load_item()
    #     yield a

