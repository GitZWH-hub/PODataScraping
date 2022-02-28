# -*- coding: utf-8 -*-
import requests
import time
import json
import random
import hashlib


def get_nounce_xyz(uri, data):
    l = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    print(len(l))
    nonce_res = []
    for i in range(9):
        idx = random.randint(0, 15)
        nonce_res.append(l[idx])

    nonce = ''.join(nonce_res)

    APP_KEY = "joker"
    res = [uri, "?AppKey=", APP_KEY, "&"]

    for key in data:
        res.append(key + "=" + data[key] + "&")

    res.append("nonce=" + nonce)
    content = ''.join(res)

    md5hash = hashlib.md5(content.encode('utf-8'))
    return nonce, md5hash.hexdigest()


# 目标url
url = "https://newrank.cn/xdnphb/main/v1/day/rank"
uri = "/xdnphb/main/v1/day/rank"

# 使用Cookie，跳过登陆操作
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
}

"""
需要提交的data
以下个别字段是否一定需要还未验证。
这里主要爬取的是日榜，所以start和end日期是一致的

"""


def get_daily_rank(end=None, start=None, rank_name=None, rank_name_group=None):
    data = {
        "end": "2022-02-21",
        "rank_name": "文化",
        "rank_name_group": "生活",
        "start": "2022-02-21",
    }
    if end is not None and start is not None and start == end:
        data["end"] = end
        data["start"] = start
    if rank_name is not None:
        data["rank_name"] = rank_name
    if rank_name_group is not None:
        data["rank_name_group"] = rank_name_group
    nonce, xyz = get_nounce_xyz(uri, data)
    print("nonce is {}".format(nonce))
    print("xyz is {}".format(xyz))

    data["nonce"] = nonce
    data["xyz"] = xyz


    # 使用get方法进行提交
    content_json = requests.post(url, headers=headers, params=data).json()
    print(content_json)
    # 返回了一个json，里面是每一页的数据
    # for item in content_json["app_msg_list"]:
    #     # 提取每页文章的标题及对应的url
    #     print(item["title"], "url: " + item["link"])
    res = []
    for item in content_json["value"]["datas"]:
        # print(item["name"], item["biz_info"])
         res.append((item["name"], item["biz_info"]))

    return res


if __name__ == "__main__":
    # print(get_daily_rank())
    # for name, biz_info in next(get_daily_rank()):
    #     print(name, biz_info)
        # print(x)
        # print(type(x))
    res = get_daily_rank()
    print(res)
