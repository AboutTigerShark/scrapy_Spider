# -*- coding: utf-8 -*-
import datetime

import scrapy
import re
from scrapy.http import Request
from urllib import parse
from items import JobBoleArticleItem, ArticleItemLoader
from util.common import get_md5
from scrapy.loader import ItemLoader

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        # 1.获取所有的url给scrapy下载后并解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            post_url = post_node.css("::attr(href)").extract_first("")
            image_url = post_node.css("img::attr(src)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url}, callback=self.parse_detail)  # yield关键字自动将url交给scrapy下载

        # 2.获取下一页的url并交给scrapy进行下载,下载完交给parse(这里是通过两个class name来定位一个节点)
        next_url = response.css(".next.page-numbers ::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

    def parse_detail(self, response):
        article_item = JobBoleArticleItem()

        # xpath选择器,提取文章的具体字段
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        # creat_data = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first().strip().replace("·", "")
        # praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract_first()
        # fav_nums = response.xpath('//span[contains(@class,"bookmark-btn ")]/text()').extract_first()
        # match_re = re.match(".*?(\d+).*", "fav_nums")
        # if match_re:
        #     fav_nums = match_re.group(1)
        # comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first()
        # match_re = re.match(".*?(\d+).*", "comment_nums")
        # if match_re:
        #     comment_nums = match_re.group(1)
        # content = response.xpath('//div[@class="entry"]').extract_first()
        # tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # # endswith() 方法用于判断字符串是否以指定后缀结尾，如果以指定后缀结尾返回True，否则返回False
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)  # .join() 连接字符串数组,将字符串、元组、列表中的元素以指定的字符(分隔符)连接生成一个新的字符串

        # # css选择器
        # title = response.css('.entry-header h1::text').extract_first("")
        # create_data = response.css('p.entry-meta-hide-on-mobile ::text').extract_first("").strip().replace("·", "")
        # praise_nums = response.css('.vote-post-up h10::text').extract_first("")
        # fav_nums = response.css('.bookmark-btn ::text').extract_first("")
        # match_re = re.match(".*?(\d+).*", "fav_nums")
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # comment_nums = response.css('a[href="#article-comment"] ::text').extract_first("")
        # match_re = re.match(".*?(\d+).*", "comment_nums")
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        #
        # content = response.css('.entry').extract_first("")
        # tag_list = response.css('.entry-meta-hide-on-mobile a::text').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        #
        # article_item["title"] = title
        # article_item["url"] = response.url
        # article_item["url_object_id"] = get_md5(response.url)
        # # try:
        # #     create_data = datetime.datetime.strptime(create_data, "%Y/%m/%d").date()
        # # except Exception as e:
        # #     create_data = datetime.datetime.now().date()
        # article_item["create_data"] = create_data
        # article_item["praise_nums"] = praise_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["front_image_url"] = [front_image_url]
        # article_item["comment_nums"] = comment_nums
        # article_item["content"] = content
        # article_item["tags"] = tags

        # 通过item loader加载item
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_data", "p.entry-meta-hide-on-mobile ::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("fav_nums", ".bookmark-btn ::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] ::text")
        item_loader.add_css("tags", ".entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", ".entry")
        article_item = item_loader.load_item()
        yield article_item
