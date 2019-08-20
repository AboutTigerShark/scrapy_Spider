# coding:utf-8
import requests
from scrapy import Selector
import MySQLdb
conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="scrapyspider", charset="utf8")
cursor = conn.cursor()



def crawl_ips():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"}
    for i in range(1, 1986):
        re = requests.get("http://www.xicidaili.com/wt/{0}".format(i), headers=headers)
        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")

        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            all_text = tr.css("td::text").extract()
            ip = all_text[0]
            port = all_text[1]
            anonymous = all_text[4]
            ip_list.append((ip, port, anonymous, speed))

        for ip_info in ip_list:
            cursor.execute(
                "insert proxy_ip(ip, port, anonymous, speed, proxy_type) VALUES('{0}', '{1}', '{2}', {3}, 'HTTP')".format(
                    ip_info[0], ip_info[1], ip_info[2], ip_info[3]
                )
            )
            conn.commit()


class GetIp(object):
    def delete_ip(self, ip):
        delete_sql = """
                DELETE FROM proxy_ip WHERE ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        # 判断ip是否可用
        http_url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        random_sql = """
              SELECT ip, port FROM proxy_ip WHERE anonymous='高匿' ORDER BY RAND() LIMIT 1
            """  # ORDER BY RAND() LIMIT 1
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            ip_judge = self.judge_ip(ip, port)
            if ip_judge:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()


# crawl_ips()
get_ip = GetIp()
get_ip.get_random_ip()
# if __name__ == "__main__":
#     get_ip = GetIp()
#     get_ip.get_random_ip()
