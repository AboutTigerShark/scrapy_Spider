# -*- coding: utf-8 -*-
import datetime
import os
import pickle
import time

import scrapy
from mouse import move, click
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from items import LagouJobItem
from settings import BASE_DIR
from util.common import get_md5


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['http://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=r'gongsi/\d+.html'), follow=True),
        Rule(LinkExtractor(allow=r'zhaopin/.*'), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_item', follow=True),
    )

    headers = {
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "Connection",
        "Host": "www.lagou.com",
    }

    def start_requests(self):
        cookies = []
        if os.path.exists(BASE_DIR + "/ArticleSpider/cookies/lagou.cookie"):
            cookies = pickle.load(open(BASE_DIR + "/ArticleSpider/cookies/lagou.cookie", "rb"))

        # if not cookies:
        #     chrome_option = Options()
        #     chrome_option.add_argument("--disable-extensions")
        #     chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        #     browser = webdriver.Chrome(executable_path="D:/chromedriver_win32/chromedriver.exe", chrome_options=chrome_option)
        #     browser.get("https://passport.lagou.com/login/login.html")
        #     browser.find_element_by_xpath("/html/body/section/div[2]/div[1]/div[2]/form/div[1]/input").send_keys("15099831654")
        #     browser.find_element_by_xpath("/html/body/section/div[2]/div[1]/div[2]/form/div[2]/input").send_keys("as781977456")
        #     time.sleep(10)
        #     move(627, 575)
        #     click()
        #     cookies = browser.get_cookies()
        #     pickle.dump(cookies, open(BASE_DIR+"/ArticleSpider/cookies/lagou.cookie", "wb"))

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict, headers=self.headers)


    def parse_item(self, response):
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()

        itemloader = ItemLoader(item=LagouJobItem(), response=response)
        itemloader.add_value("url", response.url)
        itemloader.add_value("url_object_id", get_md5(response.url))
        itemloader.add_css("title", ".job-name span::text")
        itemloader.add_css("salary", ".job_request span::text")
        itemloader.add_css("publish_time", "ul.position-label p::text")
        itemloader.add_css("tags", "ul.position li::text")
        itemloader.add_css("job_advantage", ".job-advantage p::text")
        itemloader.add_css("job_desc", ".job_bt p::text")
        itemloader.add_css("job_addr", ".job-address a::text")
        itemloader.add_css("company_url", ".job_company ul a::attr(href)")
        itemloader.add_css("company_name", "job_company dt a img::attr(alt)")
        itemloader.add_value("crawl_time", datetime.datetime.now())
        job_item = itemloader.load_item()
        return job_item
