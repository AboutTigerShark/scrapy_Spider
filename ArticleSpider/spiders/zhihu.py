# coding:utf-8
import datetime
import re
import time
import json

import scrapy
from scrapy.loader import ItemLoader
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from mouse import move, click

from items import ZhiHuQuestionItem, ZhiHuAnswerItem
from tools.zheye import zheye
from urllib import parse
import pickle


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com']

    # 初始url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&platform=desktop&sort_by=default"

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
    }

    # start-requests是入口
    def start_requests(self):
        chrome_option = Options()
        chrome_option.add_argument("--disable-extensions")
        chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        browser = webdriver.Chrome(executable_path="D:/chromedriver_win32/chromedriver.exe", chrome_options=chrome_option)
        browser.get("https://www.zhihu.com/")
        # browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL+"a")
        # browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("15099831654")
        # browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
        # browser.find_element_by_css_selector(".SignFlow-password input").send_keys("as781977456")
        # time.sleep(3)
        # move(753, 506)
        # click()
        # browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()

        cookies = browser.get_cookies()
        pickle.dump(cookies, open("D:/py3code/ArticleSpider/ArticleSpider/cookies/taobao.cookie", "wb"))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]

        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]


    def parse(self, response):
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 提取出question的url下载后交给提取函数进行提取
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(request_url, meta={"question_id": question_id}, headers=self.headers, callback=self.parse_question)
            else:
                pass
                # 如果不是question格式的url就回调给parse
                # yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        question_id = response.meta.get("question_id", "")
        itemloader = ItemLoader(item=ZhiHuQuestionItem(), response=response)
        itemloader.add_css("title", "h1.QuestionHeader-title::text")
        itemloader.add_css("content", ".QuestionHeader-detail .RichText::text")
        itemloader.add_value("url", response.url)
        itemloader.add_value("zhihu_id", question_id)
        itemloader.add_css("answer_num", ".List-headerText span::text")
        itemloader.add_css("comments_num", ".QuestionHeader-Comment button::text")
        itemloader.add_css("watch_user_num", ".QuestionHeader-follow-status .NumberBoard-itemValue::text")
        itemloader.add_css("topics", ".QuestionHeader-topics .Popover ::text")
        question_item = itemloader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers, callback=self.parse_answer)
        # yield question_item


    def parse_answer(self, response):
        # 处理question的answer
        answer_json = json.loads(response.text)
        is_end = answer_json["paging"]["is_end"]
        # totals_answer = answer_json["paging"]["totals"]
        next_url = answer_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in answer_json["data"]:
            answer_item = ZhiHuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            yield answer_item


        # if not is_end:
            # yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)




    # def start_requests(self):
    #     chrome_option = Options()
    #     chrome_option.add_argument("--disable-extensions")
    #     chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    #
    #     browser = webdriver.Chrome(executable_path="D:/chromedriver_win32/chromedriver.exe", chrome_options=chrome_option)
    #     try:
    #         browser.maximize_window()
    #     except:
    #         pass
    #
    #     browser.get("https://www.zhihu.com/signin")
    #     browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL + "a")
    #     browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("15099831654")
    #     browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
    #     browser.find_element_by_css_selector(".SignFlow-password input").send_keys("as781977456")
    #     browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
    #     time.sleep(10)
    #     login_success = False
    #
    #     while not login_success:
    #         try:
    #             notify_menu = browser.find_element_by_class_name("AppHeader-profile")
    #             login_success = True
    #         except:
    #             pass
    #
    #         try:
    #             chineseyzm = browser.find_element_by_class_name("Captcha-chineseImg")
    #         except:
    #             chineseyzm = None
    #
    #         try:
    #             englishyzm = browser.find_element_by_class_name("Captcha-englishImg")
    #         except:
    #             englishyzm = None
    #
    #         if chineseyzm:
    #             yzm_position = chineseyzm.location  # yzm_position是一个dict
    #             x_relative = yzm_position["x"]
    #             y_relative = yzm_position["y"]
    #             relative_height = browser.execute_script(
    #                 'return window.outerHeight - window.innerHeight;'
    #             )
    #             import base64
    #             base64_text = chineseyzm.get_attribute("src")
    #             code = base64_text.replace("data:image/jpg;base64,", "").replace("%0A", "")
    #             fh = open("yzm_cn.jpeg", "wb")
    #             fh.write(base64.b64decode(code))
    #             fh.close()
    #
    #
    #             z = zheye()
    #             positions = z.Recognize('yzm_cn.jpeg')
    #             last_position = []
    #             if len(positions) == 2:
    #                 if positions[0][1] > positions[1][1]:
    #                     last_position.append([positions[1][1], positions[1][0]])
    #                     last_position.append([positions[0][1], positions[0][0]])
    #                 else:
    #                     last_position.append([positions[0][1], positions[0][0]])
    #                     last_position.append([positions[1][1], positions[1][0]])
    #                 first_yzm = (int(last_position[0][0]/2), int(last_position[0][1]/2))
    #                 second_yzm = (int(last_position[1][0]/2), int(last_position[1][1]/2))
    #                 move(x_relative + first_yzm[0], y_relative + relative_height + first_yzm[1])
    #                 click()
    #                 time.sleep(3)
    #                 move(x_relative + second_yzm[0], y_relative + relative_height + second_yzm[1])
    #                 click()
    #             else:
    #                 last_position.append([positions[0][1], positions[0][0]])
    #                 first_yzm = (int(last_position[0][0]/2), int(last_position[0][1]/2))
    #                 move(x_relative + first_yzm[0], y_relative + relative_height + first_yzm[1])
    #                 click()
    #             browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL+"a")
    #             browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("15099831654")
    #             browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
    #             browser.find_element_by_css_selector(".SignFlow-password input").send_keys("as781977456")
    #             time.sleep(3)
    #             move(762, 558)
    #             click()
    #
    #         if englishyzm:
    #             import base64
    #             base64_text = englishyzm.get_attribute("src")
    #             code = base64_text.replace("data:image/jpg;base64,", "").replace("%0A", "")
    #             fh = open("yzm_eng.jpeg", "wb")
    #             fh.write(base64.b64decode(code))
    #             fh.close()
    #
    #             from ArticleSpider.tools.YDMHTTPDemo import YDMHttp
    #             yundama = YDMHttp("helloidot1", "as781977456", 7383, "b93c150403af656aa140392b23c8ac21")
    #             code = yundama.decode("yzm_eng.jpeg", 1004, 60)
    #             while True:
    #                 if code == "":
    #                     code = yundama.decode("yzm_eng.jpeg", 1004, 60)
    #                 else:
    #                     break
    #
    #             browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[3]/div/div/div[1]/input').send_keys(Keys.CONTROL+"a")
    #             browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[3]/div/div/div[1]/input').send_keys(code[1])
    #             browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(Keys.CONTROL + "a")
    #             browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("15099831654")
    #             browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
    #             browser.find_element_by_css_selector(".SignFlow-password input").send_keys("as781977456")
    #             browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
    #
    #             time.sleep(60)





