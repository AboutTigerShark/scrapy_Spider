# coding:utf-8
import re
from urllib import parse, response
import requests
from scrapy import Selector

class dazhong(object):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"}

    def crawl_dazhong(self):
        res = requests.get("http://www.dianping.com/shop/2957647", headers=self.headers)
        selector = Selector(text=res.text)
        links = selector.css("link ::attr(href)").extract()
        for link in links:
            re_match = re.match("(.*svg.*.css)", link)
            if re_match:
                result = re_match.group(1)
                res1 = requests.get("http:{0}".format(result))
                css_str = res1.text
                css_re_match = re.match(".*?url.(//s3.*svgtextcss.*svg).*?ckground.*", css_str, re.DOTALL)
                if css_re_match:
                    css_addr = css_re_match.group(1)
                    res2 = requests.get("http:{0}".format(css_addr))
                    css_addr_content = res2.text
                    print(css_addr_content)


    def css_pojie(self, result):
        res = requests.get(parse.urljoin(result), headers=self.headers)
        selector = Selector(text=res.text)
        fh = open("D:/py3code/ArticleSpider/ArticleSpider/svg.txt", "wb")
        fh.write(selector.extract())
        fh.close()


dazhongdianping =dazhong()
dazhongdianping.crawl_dazhong()

