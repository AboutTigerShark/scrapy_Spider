# coding:utf-8
import hashlib

# python3中没有unicode类型,取而代之的是str
import re


def get_md5(url):
    if isinstance(url, str):  # 判断url是不是str类型,是就返回true
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

def get_nums(text):
    match_re = re.match(".*?(\d+).*", text)
    if match_re:
        nums = (match_re.group(1))
    else:
        nums = 0
    return nums


if __name__ == "__main__":
    print(get_md5("http://jobbole.com"))
