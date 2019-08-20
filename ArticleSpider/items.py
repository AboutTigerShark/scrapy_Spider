# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from util.common import get_nums
from settings import SQL_DATE_FORMATE, SQL_DATETIME_FORMATE

# class ArticlespiderItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass

def remove_comment_tags(value):
    if '评论' in value:
        value.remove('评论')
        return value
    else:
        return value


def date_convert(value):
    try:
        create_data = datetime.datetime.strptime(value.replace('·', '').strip(), "%Y/%m/%d").date()
    except Exception as e:
        create_data = datetime.datetime.now().date()
    return create_data


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_data = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor = Join(",")
    )

class ZhiHuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = "".join(self["url"])
        title = "".join(self["title"])
        if "content" in self:
            content = "".join(self["content"])
        else:
            content = None
        answer_num = get_nums("".join(self["answer_num"]))
        comments_num = get_nums("".join(self["comments_num"]))
        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0].replace(",", ""))
            click_num = int(self["watch_user_num"][1].replace(",", ""))
        else:
            watch_user_num = int(self["watch_user_num"][0].replace(",", ""))
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMATE)

        insert_sql = """
                       insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
                       watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
                       """
        params = (zhihu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)
        return insert_sql, params




class ZhiHuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):

        insert_sql = """
                       insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num, create_time, update_time, crawl_time) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), parise_num=VALUES(parise_num),
                        update_time=VALUES(update_time)
                       """

        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATE_FORMATE)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATE_FORMATE)
        params = (self["zhihu_id"], self["url"], self["question_id"], self["author_id"], self["content"], self["praise_num"],
                  self["comments_num"], create_time, update_time, self["crawl_time"].strftime(SQL_DATETIME_FORMATE))

        return insert_sql, params


class LagouJobItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field()
    work_years = scrapy.Field()
    degree_need = scrapy.Field()
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field()
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()

class DoubanDongManItem(scrapy.Item):
    title = scrapy.Field()
    publish_year = scrapy.Field()
    jianjie = scrapy.Field()
    director = scrapy.Field()
    rate = scrapy.Field()
    actor = scrapy.Field()
    cover_image = scrapy.Field()

    def get_insert_sql(self):
        title = "".join(self["title"])
        publish_year = "".join(self["publish_year"])
        jianjie = "".join(self["jianjie"])
        director = ",".join(self["director"])
        rate = "".join(self["rate"])
        actor = ",".join(self["actor"])
        cover_image = "".join(self["cover_image"])

        insert_sql = """
                              insert into douban_dongman(title, publish_year, jianjie, director, rate, actor, cover_image) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s)  ON DUPLICATE KEY UPDATE rate=VALUES(rate), cover_image=VALUES(cover_image)
                              """

        params = (title, publish_year, jianjie, director, rate, actor, cover_image)
        return insert_sql, params

class FabangItem(scrapy.Item):
    name = scrapy.Field()
    workplace = scrapy.Field()
    phone_num =scrapy.Field()




